def get_human_decision(recommendation: str) -> dict:
    """
    Presents the agent's recommendation to the human coordinator
    and waits for their final decision.
    Returns a dict with 'decision' and 'notes'.
    """
    print("\n" + "=" * 60)
    print("HUMAN COORDINATOR REVIEW")
    print("=" * 60)
    print("\nAgent Recommendation:")
    print(recommendation)
    print("\n" + "-" * 60)
    print("Please review the recommendation above and enter your decision.")
    print("Options: APPROVE / REJECT / CLARIFY")
    print("-" * 60)

    while True:
        decision = input("\nYour decision: ").strip().upper()
        if decision in ["APPROVE", "REJECT", "CLARIFY"]:
            break
        print("Invalid input. Please enter APPROVE, REJECT, or CLARIFY.")

    notes = input("Additional notes (optional, press Enter to skip): ").strip()

    print("\n" + "=" * 60)
    print(f"DECISION RECORDED: {decision}")
    if notes:
        print(f"NOTES: {notes}")
    print("=" * 60)

    return {
        "decision": decision,
        "notes": notes,
    }
