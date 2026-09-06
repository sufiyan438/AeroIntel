from langgraph.graph import StateGraph, END

from app.langgraph.state import GraphState
from app.langgraph.planner import AgentPlanner
from app.langgraph.evaluator import EvidenceEvaluator
from app.langgraph.recovery import RecoveryPlanner
from app.langgraph.nodes import WorkflowNodes


class AeroWorkflow:

    def __init__(self):

        # Services
        self.planner = AgentPlanner()
        self.evaluator = EvidenceEvaluator()
        self.recovery = RecoveryPlanner()
        self.nodes = WorkflowNodes()

        # Create graph
        self.workflow = StateGraph(GraphState)

        # Register nodes
        self.workflow.add_node("planner", self.planner_node)

        self.workflow.add_node("metadata", self.nodes.metadata_node)
        self.workflow.add_node("vector", self.nodes.vector_node)
        self.workflow.add_node("graph", self.nodes.graph_rag_node)
        self.workflow.add_node("hybrid", self.nodes.graph_rag_node)

        self.workflow.add_node(
            "evaluator",
            self.evaluator.evaluate_state
        )

        self.workflow.add_node(
            "recovery",
            self.recovery_node
        )

        # Entry point
        self.workflow.set_entry_point("planner")

        # --------------------------------------------------
        # Initial planner routing
        # --------------------------------------------------
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

        # --------------------------------------------------
        # Retrieval -> evaluator
        # --------------------------------------------------
        self.workflow.add_edge("metadata", END)
        self.workflow.add_edge("vector", "evaluator")
        self.workflow.add_edge("graph", "evaluator")
        self.workflow.add_edge("hybrid", "evaluator")

        # --------------------------------------------------
        # Evaluator
        # --------------------------------------------------
        self.workflow.add_conditional_edges(
            "evaluator",
            self.evaluation_decision,
            {
                "end": END,
                "recover": "recovery"
            }
        )

        # --------------------------------------------------
        # Recovery routing
        # --------------------------------------------------
        self.workflow.add_conditional_edges(
            "recovery",
            self.recovery_decision,
            {
                "vector": "vector",
                "graph": "graph",
                "hybrid": "hybrid",
                "end": END
            }
        )

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

    def evaluation_decision(self, state: GraphState):

        if state["evidence_sufficient"]:
            return "end"

        # Only one recovery attempt
        if state["retry_count"] >= 1:
            print("\nMaximum recovery attempts reached.")
            return "end"

        return "recover"

    def recovery_node(self, state: GraphState):

        decision = self.recovery.recover(
            question=state["question"],
            current_route=state["route"],
            documents=state.get("documents", []),
            graph_evidence=state.get("graph_evidence", []),
            retry_count=state["retry_count"]
        )

        state["recovery_action"] = decision["action"]
        state["retry_count"] += 1

        print("\nRecovery Planner:")
        print("Action:", decision["action"])
        print("Reason:", decision["reason"])
        print("Retry count:", state["retry_count"])

        return state

    def recovery_decision(self, state: GraphState):

        action = state["recovery_action"]

        if action == "retry_vector":
            state["route"] = "vector"
            return "vector"

        if action == "retry_graph":
            state["route"] = "graph"
            return "graph"

        if action == "retry_hybrid":
            state["route"] = "hybrid"
            return "hybrid"

        return "end"