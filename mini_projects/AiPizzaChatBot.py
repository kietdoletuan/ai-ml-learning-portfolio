PIZZA_MENU = {
    "hải sản" : {"nhỏ" : 150, "vừa": 200, "lớn": 300},
    "thập cẩm" : {"nhỏ": 200, "vừa": 250, "lớn": 350}
}

SYNONYMS = {
    "wait" : {
        "greetings" : ["xin chào", "chào", "hi", "hello", "xin chao", "chao"],
    },
    "menu" : {
        "hải sản" : ["seafood", "hải sản", "1", "pizza hải sản"],
        "thập cẩm" : ["mixed", "thập cẩm", "pizza thập cẩm", "2"],
    },
    "size" : {
        "nhỏ" : ["small", "S", "1", "nhỏ"],
        "vừa" : ["medium", "M", "med", "2", "vừa"],
        "lớn" : ["large", "L", "3", "lớn"],
    },
    "confirm" : {
        "yes" : ["yes", "có", "ok", "co", "y"],
        "no" : ["no", "không", "ko", "not ok", "khong", "n"]
    },
    "check" : {
        "yes" : ["yes", "có", "ok", "co", "y"],
        "no" : ["no", "không", "ko", "not ok", "khong", "n"]
    },
    "quit" : ["tạm biệt", "thoát", "quit", "goodbye", "tam biet"],
}




def normalize_input(user_input, status):
    text = user_input.strip().lower()
    state = status["current_state"]

    if text in SYNONYMS["quit"]:
            return "quit"
    

    for key, values in SYNONYMS.items():
        if state == key:
            for i, v in values.items():
                if text in v:
                    return i
                
                
    return text

def get_greetings():
    menu = "\n".join([f"[{i}] {v}" for i, v in enumerate(PIZZA_MENU.keys(), 1)])
    return f"Heres the menu:\n\n{menu}\n\nIs there anything that you like?\n{"="*50}"

def get_prices(type):
    sizes = "\n".join([f"[{i}] {k}: {v}" for i, (k,v) in enumerate(PIZZA_MENU[type].items(), 1)])
    return f"Heres the available sizes for {type}:\n\n{sizes}\n\nWhat is your choice?\n{"="*50}"

def get_confirm_current_order(order):
    current_order = "\n".join([f"{i.title()}: {v}" for i, v in order.items()])
    return f"Let's go through your concurrent order:\n\n{current_order}\n\nIs this correct?\n{"="*50}"

def get_current_bill(status):
    orders = status["all_orders"]
    sum = 0
    for v in orders:
        sum += v["price"]
    bill = "\n".join([f"{i} | Pizza {v["type"]} ({v["size"]}) for {v["price"]}" for i, v in enumerate(orders, 1)])
    status["total"] = sum
    return f"Your current bill looks like:\n\n{bill}\n{"-"*20}\nTotal: {sum}\nWould you like to check out?\n{"="*50}"

def get_response(user_input, status):
    response = f"Try again bro\n\n\n{"="*50}"

    order = status["current_order"]
    orders = status["all_orders"]
    state = status["current_state"]
    normalized_input = normalize_input(user_input, status)

    if normalized_input == "quit":
        status["current_state"] = "quit"
        return f"Goodbye bro\n\n\n{"="*50}", status
    
    if state == "wait":
        if normalized_input == "greetings":
            order = {}
            status["current_state"] = "menu"
            response = get_greetings()
    
    elif state == "menu":
        if normalized_input in (PIZZA_MENU.keys()):
            status["current_state"] = "size"
            order["type"] = normalized_input
            response = get_prices(normalized_input)
    
    elif state == "size":
        if normalized_input in list(PIZZA_MENU[order["type"]].keys()):
            status["current_state"] = "confirm"
            order["size"] = normalized_input
            order["price"] = PIZZA_MENU[order["type"]][order["size"]]
            response = get_confirm_current_order(order)

    elif state == "confirm":
        if normalized_input == "yes":
            status["current_state"] = "check"
            orders.append(order.copy())
            status["all_orders"] = orders
            order = {}
            response = get_current_bill(status)

        elif normalized_input == "no":
            status["current_state"] = "menu"
            response = get_greetings()
    
    elif state == "check":
        if normalized_input == "yes":
            status["current_state"] = "wait"
            response = f"That will be {status["total"]}\n\nThank you for coming! \n{"="*50}\nWhat can i do for you today?\nTo start please enter greetings Hi or xi chao\n\n\n{"="*50}"
            status["total"] = 0           
            orders = {}
        elif normalized_input == "no":
            status["current_state"] = "menu"
            response = get_greetings()
            
    return response, status



def main():
    status = {
        "current_order" : {},
        "all_orders" : [],
        "current_state" : "wait",
        "total" : 0
    }
    print("=" * 50)
    print("What can i do for you today?")
    print("To start please enter greetings Hi or xi chao")
    print("\n\n\n")
    print("=" * 50)

    while True:


        userinput = input("Prompt: ") 

        response, status = get_response(userinput, status)

        print(f"Reponse: {response}")

        if status["current_state"] == "quit":
            break

if __name__ == "__main__":
    main()
