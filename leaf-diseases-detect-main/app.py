import logging
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from utils import convert_image_to_base64_and_test, summarize_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LeafCare AI API", version="1.1.0")


@app.post("/disease-detection-file")
async def disease_detection_file(file: UploadFile = File(...)):
    """Analyze an uploaded leaf image and return a structured health report."""
    try:
        logger.info("Received image file for disease detection")

        if not file.filename:
            raise HTTPException(status_code=400, detail="Please include a file name.")

        if file.content_type and "image" not in file.content_type:
            raise HTTPException(status_code=400, detail="Only image files are supported.")

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image is too large. Please use a smaller image.")

        result = convert_image_to_base64_and_test(contents)
        if result is None:
            return JSONResponse(
                status_code=502,
                content={
                    "disease_detected": False,
                    "disease_name": None,
                    "disease_type": "analysis_error",
                    "severity": "unknown",
                    "confidence": 0,
                    "symptoms": ["The analysis service could not be reached."],
                    "possible_causes": ["Temporary service issue or missing API key"],
                    "treatment": ["Please retry in a few moments."],
                    "quick_summary": "The analysis service could not be reached. Please try again shortly.",
                    "service": "LeafCare AI",
                    "status": "error",
                },
            )

        result["quick_summary"] = summarize_result(result)
        result["service"] = "LeafCare AI"
        result["status"] = "ok"
        logger.info("Disease detection from file completed successfully")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in disease detection (file): {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}") from exc


@app.get("/")
async def root():
    """Return metadata describing the API."""
    return {
        "message": "LeafCare AI leaf health analysis API",
        "version": "1.1.0",
        "service": "LeafCare AI",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)",
            "health": "/health (GET)",
        },
    }


@app.get("/health")
async def health():
    """Simple health endpoint for deployment checks."""
    return {"status": "ok", "service": "LeafCare AI API", "version": "1.1.0"}
