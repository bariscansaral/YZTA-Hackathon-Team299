from crewai import Crew, Process
from app.agents.oracle_agent import oracle_agent, forecast_task
from app.agents.supply_chain_agent import supply_chain_agent, supply_task
from app.agents.marketing_agent import marketing_agent, marketing_task
from app.agents.gatekeeper_agent import gatekeeper_agent, gatekeeper_task





forecast_task.context = [gatekeeper_task]
supply_task.context = [forecast_task]
marketing_task.context = [gatekeeper_task, forecast_task, supply_task]

integrated_crew = Crew(
    agents=[
        gatekeeper_agent,
        oracle_agent,
        supply_chain_agent,
        marketing_agent
    ],
    tasks=[
        gatekeeper_task,
        forecast_task,
        supply_task,
        marketing_task
    ],
    process=Process.sequential,
    verbose=True,
    max_rpm=10
)