def categorize_transaction(description):
    description = description.lower()

    if "swiggy" in description or "zomato" in description:
        return "Food"
    elif "uber" in description or "petrol" in description:
        return "Transport"
    elif "amazon" in description:
        return "Shopping"
    elif "electricity" in description:
        return "Utilities"
    elif "salary" in description:
        return "Income"
    else:
        return "Other"
