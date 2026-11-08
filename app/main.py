from io import BytesIO
import gc
import face_recognition
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
import numpy as np
from PIL import Image
import requests  # Thay thế urllib bằng requests

app = FastAPI()


@app.post("/api/verify-face")
async def verify_face(
    profile_image_url: str = Form(...), camera_image: UploadFile = File(...)
):
    img_profile = None
    img_camera = None
    encodings_profile = None
    encodings_camera = None

    try:
        response = requests.get(profile_image_url, timeout=10)
        response.raise_for_status()

        pil_image = Image.open(BytesIO(response.content)).convert("RGB")
        img_profile = np.array(pil_image)

        camera_bytes = await camera_image.read()
        img_camera = face_recognition.load_image_file(BytesIO(camera_bytes))

        encodings_profile = face_recognition.face_encodings(img_profile)
        encodings_camera = face_recognition.face_encodings(img_camera)

        if len(encodings_profile) == 0:
            return {"match": False, "message": "Ảnh profile không có mặt!"}

        if len(encodings_camera) == 0:
            return {"match": False, "message": "Camera không bắt được mặt!"}

        results = face_recognition.compare_faces(
            [encodings_profile[0]], encodings_camera[0], tolerance=0.5
        )

        return {"match": bool(results[0])}

    except Exception as e:
        print(f"❌ Lỗi xử lý khuôn mặt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            del img_profile, img_camera, encodings_profile, encodings_camera
        except NameError:
            pass
        gc.collect()
