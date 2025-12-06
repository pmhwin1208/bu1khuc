import pika
import csv
import sqlite3
import json
import time
import sys
import os

def send_message(channel, data_dict):
    """Gửi message đến RabbitMQ và in log rõ ràng."""
    try:
        message = json.dumps(data_dict, ensure_ascii=False)
        channel.basic_publish(
            exchange='',
            routing_key='data_queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        label = data_dict.get("ten") or data_dict.get("Ten_SP") or "..."
        print(f"📤 Đã gửi → {label}")
        return True

    except Exception as e:
        print(f"❌ Lỗi gửi message: {e}")
        return False


def connect_rabbitmq():
    """Kết nối RabbitMQ cơ bản."""
    while True:
        try:
            print("🔌 Đang kết nối RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq", port=5672)
            )
            channel = connection.channel()
            channel.queue_declare(queue="data_queue", durable=True)
            print("✅ Đã kết nối RabbitMQ.")
            return connection, channel
        except:
            print("⚠️ RabbitMQ chưa sẵn sàng, thử lại sau 3s...")
            time.sleep(3)


def main():
    # --- Kết nối RabbitMQ ---
    connection, channel = connect_rabbitmq()
    conn = None

    try:
        # --- Kết nối SQLite ---
        print("📘 Kết nối SQLite...")
        conn = sqlite3.connect("/app/data/database_nhanvien.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ============================
        # 1️⃣ GỬI TOÀN BỘ NHÂN VIÊN
        # ============================
        print("\n=== 📡 GỬI DỮ LIỆU NHÂN VIÊN ===")
        cursor.execute("SELECT * FROM ttNhanVien")
        nhanvien_rows = cursor.fetchall()

        for nv in nhanvien_rows:
            nv_dict = dict(nv)

            # Lấy khu vực
            if nv_dict.get("id_khu_vuc"):
                cursor.execute("SELECT ten_khu_vuc FROM khu_vuc WHERE id=?",
                               (nv_dict["id_khu_vuc"],))
                row = cursor.fetchone()
                nv_dict["ten_khu_vuc"] = row["ten_khu_vuc"] if row else None
            else:
                nv_dict["ten_khu_vuc"] = None

            # Lấy mặt hàng
            if nv_dict.get("id_mat_hang"):
                cursor.execute("SELECT ten_hang FROM mat_hang WHERE id=?",
                               (nv_dict["id_mat_hang"],))
                row = cursor.fetchone()
                nv_dict["ten_mat_hang"] = row["ten_hang"] if row else None
            else:
                nv_dict["ten_mat_hang"] = None

            # Lấy ngày nghỉ
            cursor.execute("SELECT * FROM ttNghi WHERE id_nhan_vien=?",
                           (nv_dict["id"],))
            nv_dict["ngay_nghi"] = [dict(r) for r in cursor.fetchall()]

            nv_dict["source"] = "sqlite"

            send_message(channel, nv_dict)

        print("✅ Đã gửi toàn bộ nhân viên.\n")

        # ============================
        # 2️⃣ GỬI TOÀN BỘ CSV
        # ============================
        print("=== 📡 GỬI DỮ LIỆU DOANH THU (CSV) ===")
        csv_path = "/app/data/doanhthu.csv"

        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row["source"] = "csv"
                    send_message(channel, row)
        else:
            print(f"⚠️ Không tìm thấy file CSV: {csv_path}")

        print("✅ Đã gửi toàn bộ dữ liệu CSV.")

    except Exception as e:
        print(f"❌ Lỗi trong quá trình gửi: {e}")

    finally:
        if connection and connection.is_open:
            connection.close()
            print("🔚 Đóng kết nối RabbitMQ.")

        if conn:
            conn.close()
            print("🔚 Đóng kết nối SQLite.")


if __name__ == "__main__":
    main()
