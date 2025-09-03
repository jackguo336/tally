from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Union
import time

from tally.models.validation.club_feed import (
    Athlete,
    ActivityStatsEntry,
    FeedActivity,
    RowData,
    CursorData,
    FeedEntrySingleActivity,
    FeedEntryMultipleActivities,
    FeedResponsePagination,
    FeedResponse,
)


def create_athlete(
    athlete_id: str | None = None,
    athlete_name: str | None = None,
) -> Athlete:
    return Athlete(
        athleteId=athlete_id or str(uuid4()), athleteName=athlete_name or "Test Athlete"
    )


def create_activity_stats_entry(
    key: str | None = None,
    value: str | None = None,
) -> ActivityStatsEntry:
    return ActivityStatsEntry(key=key or "distance", value=value or "5.2 km")


def create_feed_activity(
    id: str | None = None,
    athlete: Athlete | None = None,
    activity_name: str | None = None,
    start_date: str | None = None,
    elapsed_time: int | None = None,
    stats: List[ActivityStatsEntry] | None = None,
    activity_type: str | None = None,
) -> FeedActivity:
    return FeedActivity(
        id=id or str(uuid4()),
        athlete=athlete or create_athlete(),
        activityName=activity_name or "Test Activity",
        startDate=start_date or datetime.now(timezone.utc).isoformat(),
        elapsedTime=elapsed_time or 3600,
        stats=stats or [create_activity_stats_entry()],
        type=activity_type or "Run",
    )


def create_row_data(
    activities: List[FeedActivity] | None = None,
) -> RowData:
    return RowData(activities=activities or [create_feed_activity()])


def create_cursor_data(
    updated_at: int | None = None,
) -> CursorData:
    return CursorData(updated_at=updated_at or int(time.time()))


def create_feed_entry_single_activity(
    cursor_data: CursorData | None = None,
    activity: FeedActivity | None = None,
) -> FeedEntrySingleActivity:
    return FeedEntrySingleActivity(
        cursorData=cursor_data or create_cursor_data(),
        activity=activity or create_feed_activity(),
    )


def create_feed_entry_multiple_activities(
    cursor_data: CursorData | None = None,
    row_data: RowData | None = None,
) -> FeedEntryMultipleActivities:
    return FeedEntryMultipleActivities(
        cursorData=cursor_data or create_cursor_data(),
        rowData=row_data or create_row_data(),
    )


def create_feed_response_pagination(
    has_more: bool | None = None,
) -> FeedResponsePagination:
    return FeedResponsePagination(hasMore=has_more if has_more is not None else False)


def create_feed_response(
    entries: (
        List[Union[FeedEntrySingleActivity, FeedEntryMultipleActivities]] | None
    ) = None,
    pagination: FeedResponsePagination | None = None,
) -> FeedResponse:
    return FeedResponse(
        entries=entries or [create_feed_entry_single_activity()],
        pagination=pagination or create_feed_response_pagination(),
    )


def get_raw_club_feed() -> str:
    return (
        """
{
   "entries":[
      {
         "viewingAthlete":{
            "id":"999000001",
            "name":"John TestViewer",
            "avatarUrl":"https://example.com/test-avatar-1.png",
            "memberType":""
         },
         "entity":"Activity",
         "activity":{
            "stats":[
               {
                  "key":"stat_one",
                  "value":"30\\u003cabbr class='unit' title='minute'\\u003em\\u003c/abbr\\u003e 28\\u003cabbr class='unit' title='second'\\u003es\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_one_subtitle",
                  "value":"Time",
                  "value_object":null
               },
               {
                  "key":"stat_two",
                  "value":"99\\u003cabbr class='unit' title='beats per minute'\\u003e bpm\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_two_subtitle",
                  "value":"Avg HR",
                  "value_object":null
               },
               {
                  "key":"stat_three",
                  "value":"75\\u003cabbr class='unit' title='Calorie'\\u003e Cal\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_three_subtitle",
                  "value":"Cal",
                  "value_object":null
               }
            ],
            "description":null,
            "descriptionMentionedAthleteIds":[
               
            ],
            "descriptionMentionsClubIds":[
               
            ],
            "flagged":null,
            "activityName":"Morning Pilates",
            "id":"888000001",
            "ownedByCurrentAthlete":false,
            "segAndBestEffortAchievements":[
               
            ],
            "powerAndSegmentGoalAchievements":[
               
            ],
            "type":"Pilates",
            "mapVisPrompt":{
               
            },
            "maharajAchievement":null,
            "isVirtual":false,
            "isCommute":false,
            "workoutType":null,
            "tags":null,
            "privacyTagKey":null,
            "shareable":true,
            "twitterUrl":"https://twitter.com/intent/tweet?text=Jane T went for a 0 kilometer Workout.\\u0026url=https%3A%2F%2Fwww.strava.com%2Factivities%2F888000001%3Futm_content%3D777000001%26utm_medium%3Dreferral%26utm_source%3Dtwitter\\u0026hashtags=strava",
            "isBoosted":false,
            "visibility":"everyone",
            "athlete":{
               "avatarUrl":"https://example.com/test-avatar-jane.png",
               "athleteName":"Jane TestUser",
               "athleteId":"777000001",
               "memberType":"premium",
               "title":"\\u003ca class=\\"entry-owner\\" href=\\"/athletes/777000001\\"\\u003eJane TestUser\\u003c/a\\u003e",
               "sex":"F",
               "firstName":"Jane"
            },
            "mapAndPhotos":{
               
            },
            "timeAndLocation":{
               "timestampFormat":"date_at_time",
               "displayDateAtTime":"1 September 2025",
               "displayDate":"1 September 2025",
               "location":null
            },
            "kudosAndComments":{
               "canKudo":true,
               "hasKudoed":false,
               "highlightedKudosers":[
                  
               ],
               "kudosCount":0,
               "commentsEnabled":true,
               "comments":[
                  
               ]
            },
            "hiddenStatIndicatorString":null,
            "embedDropdownEnabled":true,
            "activityContextHeader":null,
            "activitySuggestionType":null,
            "startDate":"2025-09-01T14:54:19Z",
            "elapsedTime":1828
         },
         "cursorData":{
            "updated_at":1756740287,
            "rank":1756740287.0
         },
         "callbacks":null
      },
      {
         "viewingAthlete":{
            "id":"999000001",
            "name":"John TestViewer",
            "avatarUrl":"https://example.com/test-avatar-1.png",
            "memberType":""
         },
         "entity":"Activity",
         "activity":{
            "stats":[
               {
                  "key":"stat_one",
                  "value":"0.34\\u003cabbr class='unit' title='kilometers'\\u003e km\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_one_subtitle",
                  "value":"Distance",
                  "value_object":null
               },
               {
                  "key":"stat_two",
                  "value":"12\\u003cabbr class='unit' title='meters'\\u003e m\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_two_subtitle",
                  "value":"Elev Gain",
                  "value_object":null
               },
               {
                  "key":"stat_three",
                  "value":"11\\u003cabbr class='unit' title='minute'\\u003em\\u003c/abbr\\u003e 12\\u003cabbr class='unit' title='second'\\u003es\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_three_subtitle",
                  "value":"Time",
                  "value_object":null
               }
            ],
            "description":null,
            "descriptionMentionedAthleteIds":[
               
            ],
            "descriptionMentionsClubIds":[
               
            ],
            "flagged":null,
            "activityName":"Evening Ride",
            "id":"888000002",
            "ownedByCurrentAthlete":false,
            "segAndBestEffortAchievements":[
               {
                  "id":666000001,
                  "id_string":"666000001",
                  "activity_id":888000002,
                  "name":"Biggest Climb",
                  "sprite":"icon-at-pr-1",
                  "featured":true,
                  "elapsed_time":"13\\u003cabbr class='unit' title='second'\\u003es\\u003c/abbr\\u003e",
                  "description":"Best estimated Biggest Climb effort",
                  "distance_based_best_effort":false,
                  "hidden":false
               },
               {
                  "id":666000002,
                  "id_string":"666000002",
                  "activity_id":888000002,
                  "name":"Longest Ride",
                  "sprite":"icon-at-pr-3",
                  "featured":false,
                  "elapsed_time":"5:40",
                  "description":"3rd best estimated Longest Ride effort",
                  "distance_based_best_effort":false,
                  "hidden":false
               },
               {
                  "id":666000003,
                  "id_string":"666000003",
                  "activity_id":888000002,
                  "name":"Elevation Gain",
                  "sprite":"icon-at-pr-3",
                  "featured":false,
                  "elapsed_time":"12\\u003cabbr class='unit' title='second'\\u003es\\u003c/abbr\\u003e",
                  "description":"3rd best estimated Elevation Gain effort",
                  "distance_based_best_effort":false,
                  "hidden":false
               }
            ],
            "powerAndSegmentGoalAchievements":[
               
            ],
            "type":"Ride",
            "mapVisPrompt":{
               
            },
            "maharajAchievement":{
               "type":"all_time_best_effort",
               "image":"//d3nn82uaxijpm6.cloudfront.net/assets/svg/icon-best-effort-01-2c26b80ca16922e09eb445a74d004e2a317dbeb72d91755aa42c211e501194c4.svg",
               "image_caption":"All Time Best Effort - Biggest Climb",
               "text":"This was Bob TestAthlete's biggest climb!",
               "url":"https://www.strava.com/activities/888000002",
               "analytics":{
                  "achievement_type":"all_time_best_effort",
                  "best_effort_id":666000001,
                  "distance":null,
                  "elapsed_time":13.399999999999977,
                  "rank":1
               }
            },
            "isVirtual":false,
            "isCommute":false,
            "workoutType":null,
            "tags":null,
            "privacyTagKey":null,
            "shareable":true,
            "twitterUrl":"https://twitter.com/intent/tweet?text=Bob TestAthlete went for a 0.3 kilometer Ride.\u0026url=https%3A%2F%2Fwww.strava.com%2Factivities%2F888000002%3Futm_content%3D777000002%26utm_medium%3Dreferral%26utm_source%3Dtwitter\u0026hashtags=strava",
            "isBoosted":false,
            "visibility":"everyone",
            "athlete":{
               "avatarUrl":"https://example.com/test-avatar-bob.png",
               "athleteName":"Bob TestAthlete",
               "athleteId":"777000002",
               "memberType":"",
               "title":"\\u003ca class=\\"entry-owner\\" href=\\"/athletes/777000002\\"\\u003eBob TestAthlete\\u003c/a\\u003e",
               "sex":"M",
               "firstName":"Bob"
            },
            "mapAndPhotos":{
               
            },
            "timeAndLocation":{
               "timestampFormat":"date_at_time",
               "displayDateAtTime":"30 August 2025",
               "displayDate":"30 August 2025",
               "location":null
            },
            "kudosAndComments":{
               "canKudo":true,
               "hasKudoed":false,
               "highlightedKudosers":[
                  {
                     "destination_url":"strava://athletes/777000003",
                     "display_name":"Mike TestFan",
                     "avatar_url":"https://example.com/test-avatar-mike.png",
                     "show_name":false
                  },
                  {
                     "destination_url":"strava://athletes/777000004",
                     "display_name":"Sarah TestSupporter",
                     "avatar_url":"https://example.com/test-avatar-sarah.png",
                     "show_name":false
                  }
               ],
               "kudosCount":2,
               "commentsEnabled":true,
               "comments":[
                  
               ]
            },
            "hiddenStatIndicatorString":null,
            "embedDropdownEnabled":true,
            "activityContextHeader":null,
            "activitySuggestionType":null,
            "startDate":"2025-08-31T01:28:03Z",
            "elapsedTime":831
         },
         "cursorData":{
            "updated_at":1756604514,
            "rank":1756604514.0
         },
         "callbacks":null
      },
      {
         "viewingAthlete":{
            "id":"999000001",
            "name":"John TestViewer",
            "avatarUrl":"https://example.com/test-avatar-1.png",
            "memberType":""
         },
         "entity":"Activity",
         "activity":{
            "stats":[
               {
                  "key":"stat_one",
                  "value":"775\\u003cabbr class='unit' title='meters'\\u003e m\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_one_subtitle",
                  "value":"Distance",
                  "value_object":null
               },
               {
                  "key":"stat_two",
                  "value":"25\\u003cabbr class='unit' title='minute'\\u003em\\u003c/abbr\\u003e 38\\u003cabbr class='unit' title='second'\\u003es\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_two_subtitle",
                  "value":"Time",
                  "value_object":null
               },
               {
                  "key":"stat_three",
                  "value":"3:18\\u003cabbr class='unit' title='per 100 Meters'\\u003e /100m\\u003c/abbr\\u003e",
                  "value_object":null
               },
               {
                  "key":"stat_three_subtitle",
                  "value":"Pace",
                  "value_object":null
               }
            ],
            "description":null,
            "descriptionMentionedAthleteIds":[
               
            ],
            "descriptionMentionsClubIds":[
               
            ],
            "flagged":null,
            "activityName":"Afternoon Swim",
            "id":"888000003",
            "ownedByCurrentAthlete":false,
            "segAndBestEffortAchievements":[
               
            ],
            "powerAndSegmentGoalAchievements":[
               
            ],
            "type":"Swim",
            "mapVisPrompt":{
               
            },
            "maharajAchievement":null,
            "isVirtual":false,
            "isCommute":false,
            "workoutType":null,
            "tags":null,
            "privacyTagKey":null,
            "shareable":true,
            "twitterUrl":"https://twitter.com/intent/tweet?text=Alan T went for a 0.7 kilometer Swim.\\u0026url=https%3A%2F%2Fwww.strava.com%2Factivities%2F888000003%3Futm_content%3D777000005%26utm_medium%3Dreferral%26utm_source%3Dtwitter\\u0026hashtags=strava",
            "isBoosted":false,
            "visibility":"everyone",
            "athlete":{
               "avatarUrl":"https://example.com/test-avatar-Alan.png",
               "athleteName":"Alan TestSwimmer",
               "athleteId":"777000005",
               "memberType":"",
               "title":"\\u003ca class=\\"entry-owner\\" href=\\"/athletes/777000005\\"\\u003eAlan TestSwimmer\\u003c/a\\u003e",
               "sex":"M",
               "firstName":"Alan"
            },
            "mapAndPhotos":{
               
            },
            "timeAndLocation":{
               "timestampFormat":"date_at_time",
               "displayDateAtTime":"30 August 2025",
               "displayDate":"30 August 2025",
               "location":null
            },
            "kudosAndComments":{
               "canKudo":true,
               "hasKudoed":false,
               "highlightedKudosers":[
                  
               ],
               "kudosCount":0,
               "commentsEnabled":true,
               "comments":[
                  
               ]
            },
            "hiddenStatIndicatorString":null,
            "embedDropdownEnabled":true,
            "activityContextHeader":null,
            "activitySuggestionType":null,
            "startDate":"2025-08-30T21:05:24Z",
            "elapsedTime":1538
         },
         "cursorData":{
            "updated_at":1756589462,
            "rank":1756589462.0
         },
         "callbacks":null
      }
   ],
   "pagination":{
      "hasMore":true
   }
}
"""
    )