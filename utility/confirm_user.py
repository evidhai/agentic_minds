import boto3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)

USER_POOL_ID = "us-east-1_ODuUNHrC1"

def confirm_users():
    print(f"Scanning User Pool {USER_POOL_ID} for unconfirmed users...\n")
    client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        response = client.list_users(UserPoolId=USER_POOL_ID)
        users = response.get('Users', [])
        
        unconfirmed = [u for u in users if u['UserStatus'] == 'UNCONFIRMED']
        
        if not unconfirmed:
            print("✅ No unconfirmed users found.")
            print("List of all users:")
            for u in users:
                print(f" - {u['Username']} [{u['UserStatus']}]")
            return

        print(f"Found {len(unconfirmed)} unconfirmed user(s):")
        for i, u in enumerate(unconfirmed):
            print(f"{i+1}. {u['Username']} (Created: {u['UserCreateDate']})")
            
        choice = input("\nEnter the number of the user to confirm (or 'all'): ")
        
        users_to_confirm = []
        if choice.lower() == 'all':
            users_to_confirm = unconfirmed
        elif choice.isdigit() and 1 <= int(choice) <= len(unconfirmed):
            users_to_confirm = [unconfirmed[int(choice)-1]]
        else:
            print("Invalid choice.")
            return

        for u in users_to_confirm:
            print(f"Confirming {u['Username']}...")
            client.admin_confirm_sign_up(
                UserPoolId=USER_POOL_ID,
                Username=u['Username']
            )
            print(f"✅ {u['Username']} is now CONFIRMED.")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nTIP: If this is an auth error, ensure your terminal has valid AWS credentials.")

if __name__ == "__main__":
    confirm_users()
