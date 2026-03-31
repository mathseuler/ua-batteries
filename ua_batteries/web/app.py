"""Local FastAPI app for the UA Batteries frontend."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ua_batteries.main import add_optimization_to_dataframe
from ua_batteries.utils.get_file import get_file
from ua_batteries.visualization import create_optimization_visualization, export_to_excel

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="UA Batteries", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _default_request_day() -> str:
    """Return the current month as MM.YYYY."""
    return datetime.now().strftime("%m.%Y")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the landing page."""
    context = {
        "request": request,
        "defaults": {
            "request_day": _default_request_day(),
            "max_buys": 2,
            "max_sells": 2,
            "power": 50,
            "capacity": 100,
        },
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/download")
async def download_excel(
    request_day: str = Form(...),
    max_buys: int = Form(...),
    max_sells: int = Form(...),
    power: float = Form(...),
    capacity: float = Form(...),
):
    """Run the optimizer and return the Excel workbook."""
    try:
        df = get_file(month_year=request_day)
        optimized_df = add_optimization_to_dataframe(
            df,
            max_buys=max_buys,
            max_sells=max_sells,
            capacity=capacity,
            power=power,
        )
        viz_df = create_optimization_visualization(optimized_df)
        title = f"Energy Trading Optimization - {request_day}"
        output_path = (
            Path(tempfile.gettempdir())
            / f"energy_optimization_{request_day.replace('.', '_')}_{max_buys}_{max_sells}_{int(power)}_{int(capacity)}.xlsx"
        )
        excel_path = export_to_excel(viz_df, df, title=title, output_path=str(output_path))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FileResponse(
        path=excel_path,
        filename=Path(excel_path).name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
