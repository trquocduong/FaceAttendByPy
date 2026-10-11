from fastapi import FastAPI, UploadFile, File, HTTPException
import face_recognition
import shutil
import tempfile
import os

app = FastAPI()

print("athor: QuocDuong")


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.post("/api/verify-face")
async def verify_face(
    profile_image: UploadFile = File(...),
    camera_image: UploadFile = File(...)
):
    profile_path = None
    camera_path = None

    try:
        # Tạo file tạm an toàn
        profile_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        camera_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        profile_path = profile_file.name
        camera_path = camera_file.name

        profile_file.close()
        camera_file.close()

        # Lưu ảnh profile
        with open(profile_path, "wb") as buffer:
            shutil.copyfileobj(
                profile_image.file,
                buffer
            )

        # Lưu ảnh camera
        with open(camera_path, "wb") as buffer:
            shutil.copyfileobj(
                camera_image.file,
                buffer
            )

        # Load ảnh
        img1 = face_recognition.load_image_file(
            profile_path
        )

        img2 = face_recognition.load_image_file(
            camera_path
        )

        # Encode khuôn mặt
        encodings1 = face_recognition.face_encodings(img1)
        encodings2 = face_recognition.face_encodings(img2)

        if len(encodings1) == 0:
            return {
                "match": False,
                "message": "Không tìm thấy khuôn mặt trong ảnh profile!"
            }

        if len(encodings2) == 0:
            return {
                "match": False,
                "message": "Không tìm thấy khuôn mặt trong ảnh camera!"
            }

        # So sánh
        results = face_recognition.compare_faces(
            [encodings1[0]],
            encodings2[0],
            tolerance=0.5
        )

        return {
            "match": bool(results[0])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Luôn xóa file tạm
        if profile_path and os.path.exists(profile_path):
            os.remove(profile_path)

        if camera_path and os.path.exists(camera_path):
            os.remove(camera_path)
