product_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "count": {"type": "number", "minimum": 0}
    },
    "required": ["id", "title", "description", "price", "count"]
}
