import streamlit as st
from PIL import Image
import io
import zipfile



st.set_page_config(page_title="Tạo Thumbnail", layout="centered")

st.title("Add Thumbnails toàn bộ sản phẩm Shondo")

# Upload banner
banner_file = st.file_uploader("Upload thumbnail", type=["png", "jpg", "jpeg", "webp"])

# Upload nhiều ảnh sản phẩm
product_files = st.file_uploader(
    "Upload sản phẩm",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

# Tỉ lệ banner
col1, col2 = st.columns(2)
with col1:
    ratio = st.number_input("Tỉ lệ banner so với chiều rộng ảnh sản phẩm (%)", value=100, step=10)
with col2:
    margin_top = st.number_input("Khoảng cách từ trên (px)", value=0, step=5)

# Tùy chọn pad
pad_option = st.checkbox("Pad thành chính xác 1200x1200 (center, nền trắng)")

# Nút xử lý
if st.button("Chạy xử lý"):
    if not banner_file or not product_files:
        st.warning("⚠️ Vui lòng chọn đủ file banner và ảnh sản phẩm.")
    else:
        with st.spinner("⏳ Đang xử lý, vui lòng chờ..."):
            # Đọc banner
            banner = Image.open(banner_file).convert("RGBA")

            # Buffer zip để lưu kết quả
            result_buffer = io.BytesIO()
            with zipfile.ZipFile(result_buffer, "w") as out_zip:
                for file in product_files:
                    img = Image.open(file).convert("RGBA")

                    # Resize banner theo tỉ lệ
                    banner_w = int(img.width * ratio / 100)
                    banner_h = int(banner.height * (banner_w / banner.width))
                    banner_resized = banner.resize((banner_w, banner_h), Image.LANCZOS)

                    # Dán banner lên ảnh
                    img.paste(banner_resized, ((img.width - banner_w) // 2, margin_top), banner_resized)

                    # Pad thành 1200x1200 nếu chọn
                    if pad_option:
                        final_img = Image.new("RGB", (1200, 1200), (255, 255, 255))
                        x = (1200 - img.width) // 2
                        y = (1200 - img.height) // 2
                        final_img.paste(img, (x, y))
                    else:
                        final_img = img.convert("RGB")

                    # Lưu vào zip
                    img_bytes = io.BytesIO()
                    final_img.save(img_bytes, format="JPEG", quality=95)
                    out_zip.writestr(f"processed_{file.name}", img_bytes.getvalue())

            result_buffer.seek(0)

        st.success("✅ Xử lý hoàn tất!")
        st.download_button(
            "📦 Tải file nén kết quả",
            data=result_buffer,
            file_name="ket_qua.zip",
            mime="application/zip",
        )
