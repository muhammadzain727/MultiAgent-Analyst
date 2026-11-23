
from fastmcp import FastMCP
from sqlalchemy import text

from database.connection import engine

# Create MCP server
mcp = FastMCP("MyFashionHub")


# Create first MCP tool
@mcp.tool()
def get_products():
    """Retrieve products from MyFashionHub database."""

    query = text("""
        SELECT product_id, product_name, category
        FROM products
        LIMIT 10
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        products = [
            dict(row._mapping)
            for row in result
        ]

    return products


# Run MCP server
if __name__ == "__main__":
    mcp.run()
