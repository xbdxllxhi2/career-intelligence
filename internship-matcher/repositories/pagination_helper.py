from InquirerPy import inquirer
import json

def paginate_list(items, page_size: int = 10):
    if not items:
        print("No jobs found.")
        return

    items = list(items)  # accept list or dict values
    total = len(items)
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        chunk = items[start:end]

        print("\n=== Page", page + 1, "===\n")

        for item in chunk:
            print(json.dumps(item, indent=4, ensure_ascii=False))

        options = []
        if start > 0:
            options.append("Previous page")
        if end < total:
            options.append("Next page")
        options.append("Exit")

        action = inquirer.select(
            message="Navigation",
            choices=options
        ).execute()

        if action == "Next page":
            page += 1
        elif action == "Previous page":
            page -= 1
        else:
            break
