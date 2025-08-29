from fastmcp import FastMCP
from scripts.sirene import search_sirene_company
import os
import pynsee

def run():
    app = FastMCP("insee-server")
    pynsee.init_conn(sirene_key=os.getenv("API_KEY"))
    @app.tool()
    async def search_company(
        company_name: str = None,
        siren: str = None,
        siret: str = None,
        fuzzy: bool = True
    ):
        """
        Recherche une entreprise dans la base SIRENE selon SIREN, SIRET ou nom.

        Args:
            company_name (str, optional): Nom de l'entreprise.
            siren (str, optional): Code SIREN.
            siret (str, optional): Code SIRET.
            fuzzy (bool): Active la recherche approximative si nom partiel.

        Returns:
            dict: Informations clés sur l'entreprise.
        """
        return search_sirene_company(company_name, siren, siret, fuzzy)

    # Lancement du serveur avec transport streamable-http
    app.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")

if __name__ == "__main__":
    run()
