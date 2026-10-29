# sets.py: unique items and fast membership tests
tags = ["support", "summarize", "support", "classify", "summarize"]
unique = set(tags)
print(sorted(unique))                 # sets have no order, so sort to display
print(len(unique), "unique tags")
print("support" in unique)            # fast membership test

allowed_tools = {"calculator", "search"}
requested = {"search", "delete_files"}
print(requested - allowed_tools)      # difference: requested but not allowed
