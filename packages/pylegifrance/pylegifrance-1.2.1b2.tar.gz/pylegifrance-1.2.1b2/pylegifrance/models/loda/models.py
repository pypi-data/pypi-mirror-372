from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from pylegifrance.models.generated.model import (
    ConsultTextResponse,
    DossierLegislatif,
    ConsultSection,
    ConsultArticle,
)


class TexteLoda(BaseModel):
    """
    Model representing a LODA text (Lois, Ordonnances, Décrets, Arrêtés).
    This is a wrapper around ConsultTextResponse.
    """

    # The wrapped ConsultTextResponse instance
    consult_response: Optional[ConsultTextResponse] = Field(None, exclude=True)

    # Fields that are not directly available in ConsultTextResponse
    titre_long: Optional[str] = Field(None, description="Titre long du texte")
    last_update: Optional[str] = Field(None, description="Date de dernière mise à jour")
    texte_html: Optional[str] = Field(None, description="Contenu HTML du texte")

    # Properties delegated to ConsultTextResponse
    @property
    def id(self) -> Optional[str]:
        """Identifiant unique du texte"""
        return self.consult_response.id if self.consult_response else None

    @property
    def cid(self) -> Optional[str]:
        """Chronical ID du texte"""
        return self.consult_response.cid if self.consult_response else None

    @property
    def titre(self) -> Optional[str]:
        """Titre du texte"""
        return self.consult_response.title if self.consult_response else None

    @property
    def date_debut(self) -> Optional[str]:
        """Date de début de la version"""
        return (
            self.consult_response.date_debut_version if self.consult_response else None
        )

    @property
    def date_fin(self) -> Optional[str]:
        """Date de fin de la version"""
        return self.consult_response.date_fin_version if self.consult_response else None

    @property
    def etat(self) -> Optional[str]:
        """État juridique du texte"""
        if not self.consult_response:
            return None

        # Check both etat and juris_state fields
        # juris_state is used when searching with fond=Fond.LODA_ETAT
        if self.consult_response.etat:
            return self.consult_response.etat
        elif self.consult_response.juris_state:
            return self.consult_response.juris_state

        return None

    @property
    def sections(self) -> Optional[List[ConsultSection]]:
        """Liste des sections de premier niveau du texte"""
        return self.consult_response.sections if self.consult_response else None

    @property
    def nor(self) -> Optional[str]:
        """Numéro NOR du texte"""
        return self.consult_response.nor if self.consult_response else None

    @property
    def dossiers_legislatifs(self) -> Optional[List[DossierLegislatif]]:
        """Liste des dossiers législatifs"""
        return (
            self.consult_response.dossiers_legislatifs
            if self.consult_response
            else None
        )

    @property
    def nature(self) -> Optional[str]:
        """Nature du texte"""
        return self.consult_response.nature if self.consult_response else None

    @property
    def resume(self) -> Optional[str]:
        """Résumé du texte"""
        return self.consult_response.resume if self.consult_response else None

    @property
    def visa(self) -> Optional[str]:
        """Visas du texte"""
        return self.consult_response.visa if self.consult_response else None

    @property
    def signers(self) -> Optional[str]:
        """Signataires du texte"""
        return self.consult_response.signers if self.consult_response else None

    @property
    def nota(self) -> Optional[str]:
        """Nota du texte"""
        return self.consult_response.nota if self.consult_response else None

    @property
    def observations(self) -> Optional[str]:
        """Observations sur le texte"""
        return self.consult_response.observations if self.consult_response else None

    @property
    def date_texte(self) -> Optional[datetime]:
        """Date de signature du texte"""
        return self.consult_response.date_texte if self.consult_response else None

    @property
    def text_abroge(self) -> Optional[bool]:
        """Indique si le texte est abrogé"""
        return self.consult_response.text_abroge if self.consult_response else None

    @property
    def articles(self) -> Optional[List[ConsultArticle]]:
        """Liste des articles du texte"""
        return self.consult_response.articles if self.consult_response else None

    @property
    def date_debut_dt(self) -> Optional[datetime]:
        """Get the start date as a datetime object."""
        if not self.date_debut:
            return None
        try:
            return datetime.fromisoformat(self.date_debut.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    @property
    def date_fin_dt(self) -> Optional[datetime]:
        """Get the end date as a datetime object."""
        if not self.date_fin:
            return None
        try:
            return datetime.fromisoformat(self.date_fin.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    @property
    def last_update_dt(self) -> Optional[datetime]:
        """Get the last update date as a datetime object."""
        if not self.last_update:
            return None
        try:
            return datetime.fromisoformat(self.last_update.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    @property
    def date_texte_dt(self) -> Optional[datetime]:
        """Get the text date as a datetime object."""
        # date_texte is already a datetime object, so we just return it
        return self.date_texte
