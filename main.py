from graph.workfow import app


question = input("\nWhat would you like to analyze? ")

initial_state = {
    "user_question": question,
    "Query": "",
    "is_valid": False,
    "validation_error": "",
    "retry_count": 0,
    "final_response": ""
}

result = app.invoke(initial_state)

print("\n========== FINAL RESULT ==========\n")

if result["is_valid"]:
    print("Generated SQL:")
    print(result["Query"])

    print("\nQuery Explanation:")
    print(result["final_response"])

else:
    print("Unable to generate valid SQL after the maximum attempts.")
    print("Last validation error:")
    print(result["validation_error"])
