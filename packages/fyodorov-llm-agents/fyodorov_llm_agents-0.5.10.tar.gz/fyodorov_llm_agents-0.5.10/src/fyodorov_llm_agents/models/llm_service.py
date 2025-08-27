from datetime import datetime
from typing import Dict, Any, List, Optional

from fyodorov_llm_agents.base_service import BaseService
from fyodorov_llm_agents.providers.provider_service import Provider
from fyodorov_llm_agents.models.llm_model import LLMModel


class LLMService(BaseService[LLMModel]):
    def __init__(self):
        super().__init__("models")
        
    def _dict_to_model(self, data: Dict[str, Any]) -> LLMModel:
        """Convert dictionary from database to LLMModel"""
        return LLMModel.from_dict(data)
    
    def _model_to_dict(self, model: LLMModel) -> Dict[str, Any]:
        """Convert LLMModel to dictionary for database"""
        return model.to_dict()
        
    async def save_model_in_db(
        self, access_token: str, user_id: str, model: LLMModel
    ) -> LLMModel:
        """Save model in database with provider resolution"""
        try:
            # Get or create provider
            provider_service = Provider()
            provider = await provider_service.get_or_create_provider(
                access_token, user_id, model.provider
            )
            
            # Update model with provider ID
            model.provider = provider.id
            
            # Use base service upsert method
            result = await self.upsert_in_db(model, access_token, user_id)
            print("Saved model", result)
            return result
            
        except Exception as e:
            print(f"Error saving model: {e}")
            raise e
    
    async def update_model_in_db(
        self, access_token: str, user_id: str, name: str, update_data: Dict[str, Any]
    ) -> LLMModel:
        """Update model by name and user_id"""
        if not user_id or not name:
            raise ValueError("Model name and User ID are required")
            
        try:
            # Find existing model first
            existing_model = await self.get_model_by_name_and_user(access_token, user_id, name)
            if not existing_model:
                raise ValueError(f"Model '{name}' not found for user {user_id}")
            
            # Update the model
            result = await self.update_in_db(existing_model.id, update_data, access_token)
            print("Updated model:", result)
            return result
            
        except Exception as e:
            print(f"Error updating model with user_id {user_id} and name {name}: {e}")
            raise e
    
    async def get_model_by_name_and_user(
        self, access_token: str, user_id: str, name: str
    ) -> Optional[LLMModel]:
        """Get model by name and user_id"""
        if not user_id or not name:
            raise ValueError("Model name and User ID are required")
            
        try:
            filters = {"user_id": user_id, "name": name}
            models = await self.get_all_in_db(
                limit=1,
                user_id=None,  # Don't double-filter by user_id
                filters=filters,
                access_token=access_token
            )
            
            return models[0] if models else None
            
        except Exception as e:
            print(f"Error fetching model {name} for user {user_id}: {e}")
            raise e
    
    async def get_models_by_user(
        self,
        access_token: str,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime = None
    ) -> List[LLMModel]:
        """Get all models for a user"""
        if created_at_lt is None:
            created_at_lt = datetime.now()
            
        return await self.get_all_in_db(
            limit=limit,
            created_at_lt=created_at_lt,
            user_id=user_id,
            access_token=access_token
        )


class LLM(LLMModel):
    """Legacy wrapper class for backward compatibility - extends LLMModel with static methods"""
    
    @staticmethod
    async def update_model_in_db(
        access_token: str, user_id: str, name: str, update: dict
    ) -> dict:
        """Legacy method for backward compatibility"""
        llm_service = LLMService()
        result = await llm_service.update_model_in_db(access_token, user_id, name, update)
        return result.to_dict()

    @staticmethod
    async def save_model_in_db(
        access_token: str, user_id: str, model: LLMModel
    ) -> dict:
        """Legacy method for backward compatibility"""
        llm_service = LLMService()
        result = await llm_service.save_model_in_db(access_token, user_id, model)
        return result.to_dict()

    @staticmethod
    async def get_model(
        access_token: str = None, 
        user_id: str = None, 
        name: str = None, 
        id: str = None
    ) -> Optional[LLMModel]:
        """Legacy method for backward compatibility"""
        llm_service = LLMService()
        
        if id:
            return await llm_service.get_in_db(id, access_token)
        elif name and user_id:
            return await llm_service.get_model_by_name_and_user(access_token, user_id, name)
        else:
            raise ValueError("Either 'id' or both 'name' and 'user_id' must be provided")

    @staticmethod
    async def get_models(
        access_token: str,
        user_id: str,
        limit: int = 10,
        created_at_lt: datetime = None
    ) -> List[LLMModel]:
        """Legacy method for backward compatibility"""
        llm_service = LLMService()
        return await llm_service.get_models_by_user(access_token, user_id, limit, created_at_lt)

    @staticmethod
    async def delete_model_in_db(
        access_token: str, id: str
    ) -> bool:
        """Legacy method for backward compatibility"""
        llm_service = LLMService()
        return await llm_service.delete_in_db(id, access_token)