import datetime
import pytz
from duckduckgo_search import DDGS  # fixed import

# Calculator tool
def calculate(expr: str):
    try:
        result = eval(expr, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Timezone tool
def get_time(city: str):
    try:
        tz = pytz.timezone(city.replace(" ", "_"))
        return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"Error: {str(e)}"

# Web search tool
def search_web(query: str):
    try:
        output = ""
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            for r in results:
                output += f"{r['title']}: {r['href']}\n"
        return output if output else "No results found."
    except Exception as e:
        return f"Error: {str(e)}"
