import pika
import json
import time
import sys

from dao.dao import DataAccessObject
from validator.row_validator import (
    validate_raw_message,
    validate_transformed,
    validate_ngay_nghi_row,
)
from transformer.transformer import transform_data
from utils.logger import record_error
from utils.csv_writer import save_clean_csv


def main():
    dao = DataAccessObject("/app/data/database_nhanvien_clean.db")
    print("[CONSUMER] ✅ DAO, STAGING & Rule Chain sẵn sàng")

    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq")
            )
            channel = connection.channel()
            channel.queue_declare(queue="data_queue", durable=True)
            channel.basic_qos(prefetch_count=1)
            print("[*] Đang chờ tin nhắn từ RabbitMQ...")

            def callback(ch, method, properties, body):
                raw_data = None
                staging_id = None
                try:
                    raw_data = json.loads(body.decode())
                    src = raw_data.get("source")

                    label = (
                        raw_data.get("ten")
                        or raw_data.get("Ten_SP")
                        or raw_data.get("Tên SP")
                        or "..."
                    )
                    print(f"[STAGING] 📩 Nhận: {label} (source={src})")

                    # 1️⃣ Lưu RAW vào STAGING
                    staging_id = dao.save_raw_message(raw_data)

                    # 2️⃣ Validate RAW
                    ok_raw, reason_raw = validate_raw_message(raw_data)
                    if not ok_raw:
                        dao.update_staging_status(
                            staging_id,
                            "FAILED",
                            error_message=reason_raw,
                        )
                        record_error(raw_data, reason_raw)
                        return

                    # 3️⃣ Transform
                    transformed = transform_data(raw_data)

                    # 4️⃣ Validate sau transform
                    ok_tr, reason_tr = validate_transformed(transformed, src)
                    if not ok_tr:
                        error_info = {
                            "raw": raw_data,
                            "transformed": transformed,
                        }
                        dao.update_staging_status(
                            staging_id,
                            "FAILED",
                            error_message=reason_tr,
                        )
                        record_error(error_info, reason_tr)
                        return

                    # 5️⃣ Load vào Data Quality Layer
                    output_table = None
                    output_id = None

                    if src == "sqlite":
                        try:
                            cccd = transformed.get("cccd")
                            emp_id = dao.get_employee_by_cccd(cccd)

                            if not emp_id:
                                emp_id = dao.save_data("ttNhanVien", transformed)
                                print("➕ Thêm nhân viên mới:", transformed["ten"], "- CCCD:", cccd)
                            else:
                                print("ℹ️ Nhân viên đã tồn tại:", transformed["ten"], "- CCCD:", cccd)

                            # Lưu ngày nghỉ sạch
                            for nghi in raw_data.get("ngay_nghi", []):
                                ngay_str = nghi.get("ngay_nghi")
                                if not ngay_str:
                                    continue

                                row_nghi = {
                                    "id_nhan_vien": emp_id,
                                    "ngay_nghi": ngay_str,
                                }

                                ok_nghi, reason_nghi = validate_ngay_nghi_row(row_nghi)
                                if not ok_nghi:
                                    record_error(
                                        {"raw": raw_data, "nghi": row_nghi},
                                        reason_nghi,
                                    )
                                    continue

                                dao.save_data("ttNghi", row_nghi)

                            print("✅ Lưu DB sạch thành công:", transformed["ten"])
                            output_table = "ttNhanVien"
                            output_id = emp_id

                        except Exception as e:
                            msg = f"Lỗi DB: {e}"
                            dao.update_staging_status(
                                staging_id, "FAILED", error_message=msg
                            )
                            record_error(raw_data, msg)
                            return

                    else:
                        # CSV → ghi doanh thu sạch
                        save_clean_csv(transformed)
                        output_table = "doanhthu_clean.csv"
                        output_id = None

                    # 6️⃣ Cập nhật STAGING = SUCCESS
                    dao.update_staging_status(
                        staging_id,
                        "SUCCESS",
                        error_message=None,
                        output_table=output_table,
                        output_id=output_id,
                    )

                except Exception as e:
                    print(f"[ERROR] Xử lý message thất bại: {e}")
                    if raw_data is not None and staging_id is not None:
                        dao.update_staging_status(
                            staging_id,
                            "FAILED",
                            error_message=str(e),
                        )
                        record_error(raw_data, f"Lỗi hệ thống: {e}")
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(
                queue="data_queue",
                on_message_callback=callback,
            )
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print("[WARN] RabbitMQ chưa sẵn sàng, thử lại sau 5s")
            time.sleep(5)
        except KeyboardInterrupt:
            print("🛑 Dừng consumer")
            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass
            sys.exit(0)


if __name__ == "__main__":
    main()
