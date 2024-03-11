import streamlit as st 
import time 
import random 
# from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os 
# from dotenv import dotenv_values
# import pandas as pd
# from pandasql import sqldf

# Set up your OpenAI API key
#config = dotenv_values(".env")
#os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
#os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
os.environ["GOOGLE_API_KEY"] = st.secrets.google_creds.GOOGLE_API_KEY

# locations_df = pd.read_csv("./data/locations.csv")
# locations = sqldf("select distinct city || ', ' || country location from locations_df")
# locations = list(locations.location.values)

initial_question = """
Hello, I can help you create a travel itinerary for your visit. Please provide me with the following details to gather the necessary information:

* What are the purpose and nature of your visit? Is it an official business trip or a family vacation?
* When are you planning to travel? Please provide the start and end dates of your trip.
* How many people will be traveling with you, including yourself?
* Are there any children in your travel group? If yes, please provide their ages.
* Where are you traveling from (origin) and to (destination)?
* Do you have any specific travel preferences, such as preferred mode of transportation, accommodation type, or budget parameters?
* What kind of activities and attractions are you interested in during your stay?
* What time of the day you have for all acitivities? This is useful in case of official trips.
* Do you have any dietary restrictions that we need to consider when planning your meals?
* How do you prefer to get around the destination location? Do you plan to rent a car, use public transportation, or hire a private driver?
* Are there any additional requests or special arrangements you would like us to include in your itinerary?

Once I have all the necessary information, I will be able to create a robust itinerary that meets your specific needs and preferences. I'll provide you with detailed information on flights, accommodation, transportation, activities, and dining options, ensuring a seamless and enjoyable visit.
"""

st.set_page_config(page_title="Your Chat App", page_icon=":speech_balloon:")
st.title("🚀 AI Zippy: Your Interactive Travel Assistant 🗨️")


def remove_top_margin():
    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=1, padding_bottom=5
        ),
        unsafe_allow_html=True
    )

def initialize_sessions():
    #Initialise the key in session state
    if "clicked" not in st.session_state:
        st.session_state.clicked = {1:False}    
        
def click_recommend(button):
    # st.session_state.page = 'recommendations'
    if "chat_history" in st.session_state:
        del st.session_state.chat_history
        
    if "messages" in st.session_state:
        del st.session_state.messages
    
    st.session_state.clicked[button] = True
        
    #show_recommendations_page()        
        
def reset_options():
    pass
    

# def click_modify_selections():
#     st.session_state.page = 'selections'
    
# def click_start_from_scratch():
#     # Reset selections and go back to the beginning
#     st.session_state.start_from_scratch = True
#     st.session_state.page = 'selections'     

def main():
    remove_top_margin()
    initialize_sessions()
    side_con = st.sidebar.container()
    travel_type = side_con.radio("Select Travel Type",
                        ["Official :computer:","Family Vacation :beach_with_umbrella:"])
    date_type = side_con.radio("Select Travel Date Type",
                        ["Specific","Flexible"])

    if date_type == "Specific":
        start_date = side_con.date_input("Enter the Start Date")
        end_date = side_con.date_input("Enter the End Date")
    else:
        no_of_days = side_con.number_input("Enter no. of days", 
                                            min_value = 1,
                                            max_value = 30,
                                            value = 1,
                                            step = 1)
        no_of_nights = side_con.number_input("Enter no. of nights", 
                                            min_value = 1,
                                            max_value = 30,
                                            value = 1,
                                            step = 1)
        plan_days_constraints = side_con.slider("Flexible for next how many weeks?",0, 10)

    no_of_adults = side_con.number_input("Adults", 
                                        min_value = 1,
                                        max_value = 50,
                                        value = 1,
                                        step = 1)
            
    no_of_children = side_con.number_input("Children", 
                                        min_value = 0,
                                        max_value = 30,
                                        value = 0,
                                        step = 1)
    # travel_origin = side_con.multiselect("Travel Origin", 
    #                                      options = locations, 
    #                                      default = None)
    # travel_destination = side_con.multiselect("Travel Destination", 
    #                                      options = locations,
    #                                      default = None)

    travel_origin = side_con.text_input("Travel Origin")
    travel_destination = side_con.text_input("Travel Destination")
    accommodation_preferences = side_con.text_area("Accommodation Preferences")
    budget_usd = side_con.number_input("Budget (US Dollars)",
                                    min_value=200,
                                    max_value = 100000,
                                    step=10
                                    )
    activities_requirement = side_con.text_area("Activities Requirement")
    dietary_requirement = side_con.text_area("Dietary Requirement")
    preferred_transporation_mode = \
        side_con.selectbox("Preferred Mode of Transport",
                           ["Public", "Private"])

    additional_requests = side_con.text_area("Additional Requests")
    # Every form must have a submit button.
    side_con.button("Submit", on_click = click_recommend, args=[1])

    if st.session_state.clicked[1]:
        print("Clicked")
                    
        travel_details = f"""
        Travel Purpose: {travel_type}"""
        if date_type == "Specific":
            travel_details+= f"""\n
            Travel Dates: 
                Start Date: {start_date}
                End Date: {end_date}        
            """
        else:
            travel_details+= f"""\n
            Travel Dates: 
                No. of Days: {no_of_days}
                No. of Nights: {no_of_nights}
                Plan Flexible for next {plan_days_constraints} weeks
            """
        travel_details+= f"""\n
        No. of Adults: {no_of_adults}
        No. of Children: {no_of_children}
        Travel Origin: {travel_origin}
        Travel Destination: {travel_destination}
        Accomodation Preferences : {accommodation_preferences}
        Budget: {budget_usd} USD
        Any Activities Preferred: {activities_requirement}
        Dietary Requirement: {dietary_requirement}
        Preferred Transporation Mode: {preferred_transporation_mode}
        Any Additional Requests: {additional_requests}
        """
        
        initial_prompt = f"""
        Create a Daywise Travel Itinerary based on the given details. If some details are missed ask and get them from the user. You need to give all travel (flights, cabs) & stay recommendations to the user based on the given budget. The Travel Itinerary should also have cost estimates wherever applicable.
        ```
        Travel Details:
        {travel_details}
        ```
        """
        
        print(travel_details)
        chat = ChatGoogleGenerativeAI(
            model="gemini-pro", convert_system_message_to_human=True)

        memoryforchat=ConversationBufferMemory()
        convo=ConversationChain(memory=memoryforchat,llm=chat,verbose=True)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history=[]    
        else:
            for message in st.session_state.chat_history:
                memoryforchat.save_context({"input":message["human"]},
                                        {"outputs":message["AI"]})

        if "message" not in st.session_state:
            print("Message not present")
            st.session_state.message = [{"role":"assistant",
                                        "content":"How can I help you?"}]
            st.session_state.message.append({"role":"user",
                                            "content":initial_prompt})        
            with st.spinner("Initiating Draft Itinerary..."):
                time.sleep(1)
                initial_response=convo.predict(input=initial_prompt)
                st.write(initial_response)
                st.session_state.message.append({"role":"assistant",
                                                "content":initial_response})
                message={'human':initial_prompt,"AI":initial_response}
                st.session_state.chat_history.append(message)            
            # st.session_state.message = \
            #     [{"role":"assistant",
            #     "content":initial_question}]
        for i, message1 in enumerate(st.session_state.message):
            if i >= 3:
                with st.chat_message(message1["role"]):
                    st.markdown(message1["content"])

        if prompt:=st.chat_input("Say Something"):
                with st.chat_message("user"):
                    st.markdown(prompt)
                    st.session_state.message.append({"role":"user",
                                                     "content":prompt})
                    
                with st.chat_message("assistant"):
                        with st.spinner("Processing..."):
                            time.sleep(1)
                            response=convo.predict(input=prompt)
                            st.write(response)
                st.session_state.message.append({"role":"assistant",
                                                 "content":response})
                message={'human':prompt,"AI":response}
                st.session_state.chat_history.append(message)
            
        # clear_chat = st.button("Clear Chat")
        # if clear_chat:
        #     if "chat_history" in st.session_state:
        #         del st.session_state.chat_history
            
        #     if "messages" in st.session_state:
        #         del st.session_state.messages        
    

# Call the main function
if __name__ == "__main__":
    main()

    
# side_con.button("Reset", on_click=reset_options)


# Initialize session state variables
# if 'page' not in st.session_state:
#     st.session_state.page = None
# if 'start_from_scratch' not in st.session_state:
#     st.session_state.start_from_scratch = False

# Page routing
# if st.session_state.page == 'selections':
#     show_selections_page()
# if st.session_state.page == 'recommendations':
#     show_recommendations_page()                