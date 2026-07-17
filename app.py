import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import io

st.set_page_config(page_title="Meesho Image Optimizer", layout="centered")

st.title("📦 Meesho Low-Shipping Image Generator")
st.write("Optimize your product images to lower estimated volumetric shipping slabs.")

# Sidebar Configuration Controls
st.sidebar.header("🔧 Optimization Settings")
canvas_size = st.sidebar.slider("Canvas Dimension (Pixels)", 500, 1200, 1000, step=100)
product_scale = st.sidebar.slider("Product Visual Scale (%)", 40, 90, 65) / 100.0

# Border Controls
enable_border = st.sidebar.checkbox("Enable Frame Shift (Border)", value=True)
border_color = st.sidebar.color_picker("Border Color", "#C00000") # Default Meesho Red
border_thickness = st.sidebar.slider("Border Thickness (px)", 10, 50, 25)

# Badge Controls
add_badges = st.sidebar.checkbox("Add Trust Badges (Algorithm Disruption)", value=True)

# File Uploader
uploaded_file = st.file_uploader("Upload Product Photo (JPG/PNG)", type=["jpg", "jpeg", "png"])

def process_image(img, size, scale, border_on, b_color, b_thick, badges_on):
    # 1. Auto-crop existing white borders to isolate the core subject
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Invert to find bounding box of non-white pixels
    bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    diff = ImageChops.difference(img, bg) if 'ImageChops' in globals() else None
    
    # Simple fallback bounding box method using grayscale threshold
    gray = img.convert('L')
    inverted = ImageOps.invert(gray)
    bbox = inverted.getbbox()
    
    if bbox:
        img = img.crop(bbox)

    # 2. Scale the product target area based on selection
    max_target_dim = int(size * scale)
    img.thumbnail((max_target_dim, max_target_dim), Image.Resampling.LANCZOS)
    
    # 3. Create new master canvas
    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    
    # Center the product on the canvas
    paste_x = (size - img.width) // 2
    paste_y = (size - img.height) // 2
    canvas.paste(img, (paste_x, paste_y), img)
    
    # 4. Apply Frame Shift Border
    draw = ImageDraw.Draw(canvas)
    if border_on:
        # Draw a thick frame around the canvas boundary
        for i in range(b_thick):
            draw.rectangle([i, i, size - 1 - i, size - 1 - i], outline=b_color)

    # 5. Programmatically generate Algorithm Disruption Badges
    if badges_on:
        # Top Right Badge (e.g., Best Seller Gold Burst Circle)
        badge_radius = int(size * 0.09)
        br_x, br_y = int(size * 0.78), int(size * 0.12)
        
        # Draw gold rosette circle
        draw.ellipse([br_x - badge_radius, br_y - badge_radius, br_x + badge_radius, br_y + badge_radius], 
                     fill=(212, 175, 55, 255), outline=(180, 140, 30, 255), width=3)
        draw.text((br_x - int(badge_radius*0.6), br_y - int(badge_radius*0.3)), "BEST\nSELLER", fill=(255,255,255,255), align="center")
        
        # Bottom Left Badge (e.g., Green Verified Ribbon)
        bl_x, bl_y = int(size * 0.12), int(size * 0.78)
        draw.ellipse([bl_x - badge_radius, bl_y - badge_radius, bl_x + badge_radius, bl_y + badge_radius], 
                     fill=(0, 150, 70, 255), outline=(0, 100, 40, 255), width=3)
        draw.text((bl_x - int(badge_radius*0.7), bl_y - int(badge_radius*0.3)), "PREMIUM\nQUALITY", fill=(255,255,255,255), align="center")

    # Convert back to RGB for final saving as JPEG
    return canvas.convert("RGB")

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(original_image, use_container_width=True)
        
    with col2:
        st.subheader("Optimized Output")
        with st.spinner("Processing image configurations..."):
            processed_img = process_image(
                original_image, canvas_size, product_scale, 
                enable_border, border_color, border_thickness, add_badges
            )
        st.image(processed_img, use_container_width=True)
        
        # Preparation for downlaod
        buffer = io.BytesIO()
        processed_img.save(buffer, format="JPEG", quality=90)
        byte_data = buffer.getvalue()
        
        st.download_button(
            label="💾 Download Optimized Image",
            data=byte_data,
            file_name="meesho_optimized_product.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
