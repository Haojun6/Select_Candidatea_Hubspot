import requests
import json
import dateutil.parser as parser
import datetime

urlGet = "https://candidate.hubteam.com"
urlPost = "https://candidate.hubteam.com"

# get the data from the url
def getData(url):
    response = requests.get(url)
    if response:
        print('Success in getting the data!')
        return response.json()
    else:
        raise RuntimeError('Fail in getting the data!')

# post the data to the url
def postData(url, data):
    response = requests.post(url, data = data)
    status = response.status_code
    if status == 200:
        print('Success in posting the data!')
    elif status == 400:
        raise RuntimeError('Fail in getting the data! Timeout!')
    else:
        raise RuntimeError(status, 'Something goes wrong!')

# the main procedures of the program
def main():
    dataGet = getData(urlGet)
    dataPost = searchAppropriateList(dataGet)
    postData(urlPost, json.dumps(dataPost))


def searchAppropriateList(data):
    # the result that will be submitted
    result = []
    # the countries exist in the data
    countriesList = {}
# partners->everyPartner->country->countriesList
    # create the space for every unique country from the list got
    for everyPartner in data["partners"]:
        if everyPartner["country"] not in countriesList:
            countriesList[everyPartner["country"]] = {}

        # create the space for each date that belongs to each country from above
        for availableDate in everyPartner["availableDates"]:
            if availableDate not in countriesList[everyPartner["country"]]:
                countriesList[everyPartner["country"]][availableDate] = []
            countriesList[everyPartner["country"]][availableDate].append(everyPartner)

    for eachCountry, everyPartnerDates in countriesList.items():
        # sort the dates to make comparison easier
        sorted_dates = sorted(everyPartnerDates.keys())
        total_attendees = 0
        begin_date = None
        attendee_most_case = []

        # select two available day in a row to check if appropriate
        for i in range(len(sorted_dates[:-1])):
            first_day = sorted_dates[i]
            second_day = sorted_dates[i + 1]
            # if the difference of two dates is greater or less than 1, not choose
            if parser.parse(second_day) - parser.parse(first_day) != datetime.timedelta(1):
                continue
            # get the attendees for each two days
            first_day_attendee = set([(el['firstName'], el['lastName'], el['email']) for el in everyPartnerDates[first_day]])
            second_day_attendee = set([(el['firstName'], el['lastName'], el['email']) for el in everyPartnerDates[second_day]])

            # the attendees that available for both days
            intersected_attendees = first_day_attendee.intersection(second_day_attendee)
            attendee_amount = len(intersected_attendees)

            # get the date that has the most attendees
            if attendee_amount > total_attendees:
                total_attendees = attendee_amount
                begin_date = first_day
                attendee_most_case = intersected_attendees
        # combine the data
        result.append({"attendeeCount": total_attendees,
                          "attendees": [x[2] for x in attendee_most_case],# just needs the email
                          "name": eachCountry,
                          "startDate": None if total_attendees == 0 else begin_date
                          })

    return {"countries": result}


main()
