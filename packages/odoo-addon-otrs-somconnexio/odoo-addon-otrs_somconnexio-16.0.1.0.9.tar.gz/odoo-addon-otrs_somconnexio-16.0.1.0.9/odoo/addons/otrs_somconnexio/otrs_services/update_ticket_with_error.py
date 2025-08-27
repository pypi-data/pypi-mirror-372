from otrs_somconnexio.services.update_ticket_with_provider_info import (
    UpdateTicketWithProviderInfo,
)
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class UpdateTicketWithError(UpdateTicketWithProviderInfo):
    """
    Update the ticket process with an article to inform about an error.

    Params:
    ticket_id (str) -> id from the involved OTRS ticket to which an article will be send
    error (dict) -> dictionary with the error description
    df_dct (dict) -> dictionary with the Dynamic Fields to be updated and their values
    """

    def __init__(self, ticket_id, error, df_dct=None):
        self.ticket_id = ticket_id
        self.article = AbstractArticle()
        self.article.subject = error.get("title", "Odoo Error")
        self.article.body = error.get("body", "Odoo Error")
        self.df_dct = df_dct or {}
