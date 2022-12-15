from bs4 import BeautifulSoup
import json
import urllib3
import os.path
from about import get_about
from locations import get_locations

'''
SI 507 Final Project
Author: Zhe Yang
Comment: the cache files are not uploaded to GitHub. If one wants to test it with the cache files, one can simply
run the program twice.
'''

EXIT = {"exit", "Exit", "EXIT", "e", "E"}
EXIT_PROMPT = "Type exit or e to exit the current order."

class Food():
    '''
    Food class of all kinds of food
    '''
    def __init__(self, name, price, description, food_type):
        self.name = name
        self.price = price
        self.description = description
        self.food_type = food_type
        
    def __str__(self):
        s = f"{self.name}\n"
        s += f"price: {self.price}\n"
        s += f"description: {self.description}\n"
        return s

        
class TreeNode():
    '''
    TreeNode that stores food and food types
    '''
    def __init__(self, food_type, food, children):
        self.food_type = food_type
        self.food = food
        self.children = children
        
    def is_leaf(self):
        return len(self.children) == 0

def get_menu():
    '''
    output: BeautifulSoup object menu, with raw menu information
    '''
    http = urllib3.PoolManager()
    url = 'https://nothai.com/menu/'
    response = http.request("GET", url)
    html_doc = response.data.decode('utf-8')
    soup = BeautifulSoup(html_doc, features="lxml")
    menu = soup.find_all("section", {"class": "menu-main-parent-row"})
    return menu
    
    
def get_food_types(fname=None, menu=None):
    '''
    input: fname, string, name of cache file
           menu, menu from get_menu()
    output: food_types, list of food types
    '''
    food_types = []
    if not fname:
        for i in range(len(menu)):
            if i == 0:
                food_types.append(menu[i].find_all("span")[2].text)
            else:
                food_types.append(menu[i].find("span").text)
        with open('food_types.txt', 'w') as f:
            for food in food_types:
                f.write(f"{food}\n")
    else:
        with open(fname, 'r') as f:
            for line in f:
                food_types.append(line.strip())
    return food_types


def get_food(food_type, fname=None, raw_list=None):
    '''
    input: food_type, string, food type from list of food types
           fname, string, name of cache file
           raw_list, raw information of food
    output: food_list, list of Food obejcts
    '''
    food_list = []
    if not fname:
        i = 0
        name = ''
        price = ''
        description = ''
        flag = 0
        while i < len(raw_list):
            if i % 3 == 0:
                name = raw_list[i].text
                num = int(name.split('.')[0])
                # there are two "19" in the official menu webpage, fix that
                if flag == 1:
                    num += 1
                    name = str(num) + '.' + name.split('.')[1]
                if num == 19:
                    flag = 1
            elif i % 3 == 1:
                price = raw_list[i].text
            else:
                description = raw_list[i].text
                food_list.append(Food(name, price, description, food_type))
            i += 1
        fname = food_type + '.txt'
        with open(fname, 'w') as f:
            for food in food_list:
                f.write(f"{food.name}\n")
                f.write(f"{food.price}\n")
                f.write(f"{food.description}\n")
    else:
        i = 0
        name = ''
        price = ''
        description = ''
        with open(fname, 'r') as f:
            for line in f:
                if i % 3 == 0:
                    name = line.strip()
                elif i % 3 == 1:
                    price = line.strip()
                else:
                    description = line.strip()
                    food_list.append(Food(name, price, description, food_type))
                i += 1
    return food_list

def get_drinks(fname=None, raw_list=None):
    '''
    input: fname, string, name of cache file
           raw_list, raw information of drinks
    output: food_list, list of Food obejcts
    '''
    food_type = 'Drinks'
    food_list = []
    if not fname:
        i = 0
        name = ''
        price = ''
        description = ''
        idx = 1
        while i < len(raw_list):
            if i % 2 == 0:
                name = raw_list[i].text
                name = str(idx) + ". " + name
                idx += 1
            else:
                if len(raw_list[i].text) > 1:
                    # Finish finding drinks
                    break
                price = raw_list[i].text
                food_list.append(Food(name, price, description, food_type))
            i += 1
        fname = food_type + '.txt'
        with open(fname, 'w') as f:
            for food in food_list:
                f.write(f"{food.name}\n")
                f.write(f"{food.price}\n")
    else:
        i = 0
        name = ''
        price = ''
        description = ''
        with open(fname, 'r') as f:
            for line in f:
                if i % 2 == 0:
                    name = line.strip()
                else:
                    price = line.strip()
                    food_list.append(Food(name, price, description, food_type))
                i += 1
    return food_list
                

def get_all_food(food_types, menu=None):
    '''
    input: food_types, list of food types from get_food_types
           menu, menu from get_menu()
    output: food_map, map from food types to list of Food objects
    '''
    food_map = {}
    i = 0
    for food_type in food_types:
        fname = food_type + '.txt'
        if food_type != 'Drinks':
            if os.path.isfile(fname):
                food_list = get_food(food_type, fname, None)
            else:
                raw_list = menu[i].find("div", {"class": "wpb_wrapper"}).find_all("p")
                food_list = get_food(food_type, None, raw_list)
            food_map[food_type] = food_list
        else:
            if os.path.isfile(fname):
                food_list = get_drinks(fname, None)
            else:
                raw_list = menu[i].find("div", {"class": "wpb_wrapper"}).find_all("p")
                food_list = get_drinks(None, raw_list)
            food_map[food_type] = food_list
        i += 1
    return food_map

def build_tree(food_types, food_map):
    '''
    input: food_types, list of food types from get_food_types
           food_map, map from food types to list of Food objects
    output: root, root node of a food tree
    '''
    root = TreeNode('Entree', None, [])
    i = 1
    if type(food_types) == list:
        for food_type in food_types:
            food_num_type = str(i) + ". " + food_type
            node = TreeNode(food_num_type, None, [])
            for food in food_map[food_type]:
                leaf = TreeNode(food.name, food, None)
                node.children.append(leaf)
            root.children.append(node)
            i += 1
    else:
        food_type = food_types
        food_num_type = str(i) + ". " + food_type
        node = TreeNode(food_num_type, None, [])
        for food in food_map[food_type]:
            leaf = TreeNode(food.name, food, None)
            node.children.append(leaf)
        root.children.append(node)
    return root

def yes(prompt):
    '''
    Acknowledge the idea in Project 2
    '''
    valid_yes = {'yes', 'Yes', 'YES', 'y', 'Y', 'yup', 'sure'}
    valid_no = {'no', 'No', 'NO'}
    print(prompt)
    answer = input()
    while True:
        if answer in valid_yes:
            return True
        elif answer in valid_no:
            return False
        else:
            print("Please answer with 'yes' or 'no'")
            answer = input()
            
def tree_interaction(node, flag):
    '''
    input: node, a TreeNode object
           flag, a control signal that controls the slight differences between different trees
    An interaction module of a tree. It can serve with 3 kinds of trees with flag equal to 0, 1 or 2
    '''
    if flag == 0:
        start = int(node.children[0].split('.')[0])
        end = int(node.children[-1].split('.')[0])
    else:
        start = int(node.children[0].food_type.split('.')[0])
        end = int(node.children[-1].food_type.split('.')[0])
    print(f"Please select the {node.food_type} that you want with the number. " + EXIT_PROMPT)
    for item in node.children:
        if flag == 0:
            print(item)
        elif flag == 1:
            print(item.food_type)
        else:
            print(item.food)
        print()
    while True:
        selection = input()
        if selection in EXIT:
            return None
        try:
            selection = int(selection)
            if selection >= start and selection <= end:
                idx = selection - start
                if flag == 0:
                    print(f"Selected food {node.children[idx]}")
                    print()
                    return node.children[idx].split('.')[1].strip()
                else:
                    print(f"Selected food {node.children[idx].food_type}")
                    print()
                    return node.children[idx]
            else:
                print("Please select with the exact number before each food. " + EXIT_PROMPT)
        except:
            print("Please select with the exact number before each food. " + EXIT_PROMPT)
    
    

def interaction(protein, spice, main_food, sides, drinks):
    '''
    input: protein, tree of protein
           spice, tree of spicy levels
           main_food, tree of main food
           sides, tree of sides
           drinks, tree of drinks
    The main interaction module for the menu and ordering part of the project.
    '''
    selected_protein = tree_interaction(protein, 0)
    if not selected_protein:
        return
    selected_spice = tree_interaction(spice, 0)
    if not selected_spice:
        return
    selected_entree = tree_interaction(main_food, 1)
    if not selected_entree:
        return
    selected_food = tree_interaction(selected_entree, 2)
    if not selected_food:
        return
    selected_sides = None
    selected_drinks = None
    price = int(selected_food.food.price)
    if selected_protein.split()[0] == "Shrimp":
        price += 1
    sides_prompt = "Would you like some sides?"
    if yes(sides_prompt):
        selected_sides = tree_interaction(sides.children[0], 2)
        if not selected_sides:
            return
        price += int(selected_sides.food.price)
    drinks_prompt = "Would you like some drinks?"
    if yes(drinks_prompt):
        selected_drinks = tree_interaction(drinks.children[0], 2)
        if not selected_drinks:
            return
        price += int(selected_drinks.food.price)

    print("You have finished your order! Your order is:")
    print(f"Protein: {selected_protein}")
    print(f"Spicy Level: {selected_spice}")
    print(f"Entree: {selected_entree.food_type}")
    print("Food:")
    print(selected_food.food)
    if selected_sides:
        print("Sides:")
        print(selected_sides.food)
    if selected_drinks:
        print("Drinks:")
        print(selected_drinks.food)
    print()
    print(f"The total price is ${str(price)}.")


def main():
    http = urllib3.PoolManager()
    # description
    fname = 'About.txt'
    if os.path.isfile(fname):
        about_text_list = get_about(fname, None)
    else:
        url_d = 'https://nothai.com/about/'
        response_d = http.request("GET", url_d)
        html_doc_d = response_d.data.decode('utf-8')
        soup_d = BeautifulSoup(html_doc_d, features="lxml")
        about = soup_d.find_all("p", {'style': False, 'id': False})
        about_text_list = get_about(None, about)
    print("Welcome to the Nothai ordering system!")
    print("About Nothai:")
    for text in about_text_list:
        print(text)
    
    # menu
    fname = 'food_types.txt'
    if os.path.isfile(fname):
        food_types = get_food_types(fname, None)
        fname_list = ['Noodles.txt', 'Stir Fry.txt', 'Fried Rice.txt', 'Sides.txt', 'Drinks.txt']
        flag = 0
        for fname in fname_list:
            if not os.path.isfile(fname):
                flag = 1
                break
        if flag == 0:
            food_map = get_all_food(food_types, None)
        else:
            menu = get_menu()
            food_map = get_all_food(food_types, menu)
    else:
        menu = get_menu()
        food_types = get_food_types(None, menu)
        food_map = get_all_food(food_types, menu)
    main_food = build_tree(food_types[:3], food_map)
    sides = build_tree(food_types[3], food_map)
    drinks = build_tree(food_types[4], food_map)
    protein = TreeNode('Protein', None, ['1.Chicken', '2.Beef', '3.Tofu', '4.Shrimp (served with $1 more)'])
    spice = TreeNode('Spicy Level', None, ['1.No Spice', '2.Weak Sauce', '3.Medium', '4.Yoga Flame', '5.Dim Mak'])
    while True:
        prompt = "Would you like to order now?"
        if not yes(prompt):
            break
        interaction(protein, spice, main_food, sides, drinks)
        
    # locations
    fname = 'Locations.txt'
    if os.path.isfile(fname):
        locations_list = get_locations(fname, None)
    else:
        url_l = 'https://nothai.com/locations/'
        response_l = http.request("GET", url_l)
        html_doc_l = response_l.data.decode('utf-8')
        soup_l = BeautifulSoup(html_doc_l, features="lxml")
        locations = soup_l.find_all("section", {'class': 'wpb_row'})
        locations_list = get_locations(None, locations[3:-1])
    print("Nothai serves at the following locations. You could go to taste something delicious!")
    for location in locations_list:
        print(location)
    print("Goodbye!")


if __name__ == '__main__':
    main()
