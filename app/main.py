import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from app.schemas import ProductInput
from app.llm_service import generate_product_card

app = FastAPI(title="AI-помощник для подготовки товарных описаний")

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>AI-помощник для подготовки товарных описаний</title>
    <style>
        body { font-family: Arial; padding: 20px; max-width: 1000px; margin: 0 auto; }
        .container { display: flex; gap: 20px; }
        .box { flex: 1; border: 1px solid #ccc; padding: 20px; border-radius: 8px; background: #fafafa; }
        input[type="text"], textarea { width: 100%; padding: 8px; margin-top: 5px; margin-bottom: 15px; box-sizing: border-box; }
        button { padding: 10px 20px; font-size: 16px; background: #0056b3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #004494; }
    </style>
</head>
<body>
    <h2>Генератор карточек товаров (B2B)</h2>

    <div class="container">
        <!-- Форма 1: Удобная для менеджера -->
        <div class="box">
            <h3>Способ 1: Форма ввода</h3>
            <form action="/generate-form" method="post">
                <label>Название товара:</label>
                <input type="text" name="name" required placeholder="Манометр DM 02">

                <label>Производитель:</label>
                <input type="text" name="manufacturer" required placeholder="Манотомь">

                <label>Описание:</label>
                <textarea name="description" rows="4" required placeholder="Прибор предназначен..."></textarea>

                <label>Характеристики (каждая с новой строки "Ключ: Значение"):</label>
                <textarea name="specs" rows="4" placeholder="диапазон: 0-1.6 МПа&#10;класс: 1.5"></textarea>

                <button type="submit">Сгенерировать</button>
            </form>
        </div>

        <!-- Форма 2: Вставка чистого JSON -->
        <div class="box">
            <h3>Способ 2: JSON (для API)</h3>
            <form action="/generate-json" method="post">
                <label>Вставьте JSON:</label>
                <textarea name="json_data" rows="14" required placeholder='{"name": "...", "manufacturer": "...", "specs": {}, "description": "..."}'></textarea>
                <button type="submit">Сгенерировать</button>
            </form>
        </div>
    </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def read_form():
    return HTML_FORM


@app.post("/generate-form", response_class=HTMLResponse)
async def generate_from_form(
        name: str = Form(...),
        manufacturer: str = Form(...),
        description: str = Form(...),
        specs: str = Form(default="")
):
    specs_dict = {}
    if specs:
        for line in specs.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                specs_dict[key.strip()] = value.strip()

    data_dict = {"name": name, "manufacturer": manufacturer, "description": description, "specs": specs_dict}
    print(data_dict)
    result_markdown = await generate_product_card(data_dict)
    return show_result(result_markdown)


@app.post("/generate-json", response_class=HTMLResponse)
async def generate_from_json(json_data: str = Form(...)):
    try:
        data_dict = json.loads(json_data)
        product = ProductInput(**data_dict)
    except Exception as e:
        return f"<h3>Ошибка в формате JSON:</h3><p>{e}</p><a href='/'>Назад</a>"
    result_markdown = await generate_product_card(product.model_dump())
    return show_result(result_markdown)


def show_result(result_markdown: str) -> str:
    return f"""
    <body style="font-family: Arial; padding: 20px; max-width: 800px; margin: 0 auto;">
        <h2>Результат генерации:</h2>
        <div style="background: #f4f4f4; padding: 20px; white-space: pre-wrap; border-radius: 8px; line-height: 1.6;">{result_markdown}</div>
        <br>
        <a href="/" style="padding: 10px 20px; background: #0056b3; color: white; text-decoration: none; border-radius: 4px;">Сгенерировать еще</a>
    </body>
    """