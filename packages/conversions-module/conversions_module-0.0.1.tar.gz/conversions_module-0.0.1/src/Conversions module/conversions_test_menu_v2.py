
from conversions_module_khan_compatible_v8 import (
    custom_designation_error,
    toggle_string_binary, toggle, toggle_with_return, toggle_with_print,
    get_designation_value, print_designation_value, list_designations, DesignationError
)

def menu():
    while True:
        print("\n--- Designation Toggle Test Menu ---")
        print("1. Save new designation")
        print("2. Toggle designation in-place")
        print("3. Toggle designation and return value")
        print("4. Toggle designation and print value")
        print("5. Get designation value (no toggle)")
        print("6. Print designation value (no toggle)")
        print("7. List all designations")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == '1':
            value = input("Enter string or binary to save: ")
            name = input("Enter designation name: ")
            result = toggle_string_binary(value, save_with_designation=True, designation=name)
            print(f"Saved: {name} → {result}")
        elif choice == '2':
            name = input("Enter designation name to toggle: ")
            try:
                toggle(name)
                print("Toggled.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '3':
            name = input("Enter designation name to toggle and return: ")
            try:
                print("Returned:", toggle_with_return(name))
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '4':
            name = input("Enter designation name to toggle and print: ")
            try:
                toggle_with_print(name, prefix="Toggled value: ")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '5':
            name = input("Enter designation name to get: ")
            try:
                print("Stored value:", get_designation_value(name))
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '6':
            name = input("Enter designation name to print: ")
            try:
                print_designation_value(name, prefix="Stored value: ")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '7':
            try:
                print("All Designations:", list_designations())
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

# Run menu if this file is executed directly
if __name__ == "__main__":
    menu()
