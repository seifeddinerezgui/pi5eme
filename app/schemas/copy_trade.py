from pydantic import BaseModel, Field


class FollowRequest(BaseModel):
    follower_id: int = Field(..., description="ID de l'utilisateur qui souhaite suivre")
    percentage_to_invest: float = Field(..., gt=0, le=1, description="Pourcentage à investir, entre 0 et 1")


class MessageResponse(BaseModel):
    message: str