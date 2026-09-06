# from langgraph.graph import StateGraph, END

# from app.langgraph.state import GraphState
# from app.langgraph.router import QueryRouter
# from app.langgraph.nodes import WorkflowNodes

# class AeroWorkflow:
#     def __init__(self):

#         #Services
#         self.router = QueryRouter()
#         self.nodes = WorkflowNodes()

#         #creating graph
#         self.workflow = StateGraph(GraphState)

#         #Registering nodes
#         self.workflow.add_node("router", self.route_node)
#         self.workflow.add_node("metadata", self.nodes.metadata_node)
#         self.workflow.add_node("vector", self.nodes.vector_node)
#         # self.workflow.add_node("graph", self.nodes.graph_node)
#         self.workflow.add_node("graph", self.nodes.graph_rag_node)

#         #Entry point
#         self.workflow.set_entry_point("router")

#         #Conditional routing
#         self.workflow.add_conditional_edges("router",
#                                             self.route_decision,
#                                             {
#                                                 "metadata": "metadata",
#                                                 "vector": "vector",
#                                                 "graph": "graph"
#                                             })

#         #END nodes
#         self.workflow.add_edge("metadata", END)
#         self.workflow.add_edge("vector", END)
#         self.workflow.add_edge("graph", END)

#         #Compile graph
#         self.app = self.workflow.compile()


#     def route_node(self, state: GraphState):
#         route = self.router.route(
#             question=state["question"],
#             scope=state["scope"]
#         )
#         state["route"] = route
#         return state

#     def route_decision(self, state: GraphState):
#         return state["route"]




from langgraph.graph import StateGraph, END

from app.langgraph.state import GraphState
from app.langgraph.planner import AgentPlanner
from app.langgraph.nodes import WorkflowNodes


class AeroWorkflow:

    def __init__(self):

        # Services
        self.planner = AgentPlanner()
        self.nodes = WorkflowNodes()

        # Create graph
        self.workflow = StateGraph(GraphState)

        # Register nodes
        self.workflow.add_node("planner", self.planner_node)
        self.workflow.add_node("metadata", self.nodes.metadata_node)
        self.workflow.add_node("vector", self.nodes.vector_node)
        self.workflow.add_node("graph", self.nodes.graph_rag_node)
        self.workflow.add_node("hybrid", self.nodes.graph_rag_node)

        # Entry point
        self.workflow.set_entry_point("planner")

        # Conditional routing
        self.workflow.add_conditional_edges(
            "planner",
            self.route_decision,
            {
                "metadata": "metadata",
                "vector": "vector",
                "graph": "graph",
                "hybrid": "hybrid"
            }
        )

        # End nodes
        self.workflow.add_edge("metadata", END)
        self.workflow.add_edge("vector", END)
        self.workflow.add_edge("graph", END)
        self.workflow.add_edge("hybrid", END)

        # Compile graph
        self.app = self.workflow.compile()

    def planner_node(self, state: GraphState):

        decision = self.planner.plan(
            question=state["question"],
            scope=state["scope"]
        )

        state["route"] = decision["strategy"]

        print("\nAgent Planner:")
        print("Strategy:", decision["strategy"])
        print("Reason:", decision["reason"])

        return state

    def route_decision(self, state: GraphState):
        return state["route"]