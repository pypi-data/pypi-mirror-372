from agents import Agent


from abc import ABC, abstractmethod

class AgentFactory(ABC):
    @abstractmethod
    def get_agent(self, agent_type: str) -> Agent:
        """
        抽象方法，用于获取指定类型的Agent实例
        
        Args:
            agent_type: Agent类型标识
            
        Returns:
            Agent实例
        """
        pass