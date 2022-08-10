# Code assignment for FTrack

## Quick Start

Rename `example.env` into `.env`.

```shell
docker compose up
```

- Dashboard is available at http://localhost:8000/dashboard
- To send events POST to http://localhost:8000/webhooks/event

Additionally there are API endpoints that return json:

- all events http://localhost:8000/events
- a specific event http://localhost:8000/events/{event_id}
- all events for a specific entity http://localhost:8000/entities/{entity_id}
- aggrigate the events for an entity to see it's current state http://localhost:8000/aggrigates/{entity_id}

## Limitations

- There are no security mesures in place.
- There is no API documentation.
- Validation is on the light side.
- Uses the Flask development server.

---

## Origonal Prompt

### Backend Case

At ftrack, we are investigating using a webhook API to allow third-party developers to listen to changes to entities in our backend.

For debugging purposes, we are interested in having a small web application that stores and displays this event data on a very simple web page.

Your task is to create such a web service.
Webhooks service

The webhook service is still in the design phase, but we have collectively agreed upon an API that you can mock. 

Here are two examples of webhook events you can expect, and should mock in your service:

POST `${webhookBaseUrl}/event`

```json
{
    "action": "create",
    "entity_type": "component",
    "time": "2021-12-20T10:59:55Z",
    "payload": {
        "id": "25589645-cd89-44bb-8954-6b4ee87aa57f",
        "name": "image name",
        "file_type": "jpeg"
    }
}
```

POST `${webhookBaseUrl}/event`

```json
{
    "action": "update",
    "entity_type": "task",
    "time": "2021-12-21T08:51:22Z",
    "id": "25589645-cd89-44bb-8954-6b4ee87aa57f",
    "modified_fields": ["assignee"],
    "payload": {
        "name": "task name",
        "assignee_id": "5428abf6-0f4c-4448-b619-fc9f4327619b"
    }
}
```

### Task requirements

- Create a webhook listener service 
- Use mocked data in the same format as specified above. You can generate and store the mocked data as part of your webhook listener.
- Store the create and update events in a database of your choice. 
- The event data should only be stored in the database for the past 7 days, and should after 7 days be deleted.
- Display the create and update events on a simple web page, set up by a web server of your choice.
- The web server should fetch data from the database and display it in a simple format on a web page.
- Remember that this is just a debugging tool — don’t spend too much time on making it pretty. :)
- Make everything easy to set up and run using docker-compose.
- Ideally, you should be able to run the application with docker-compose up and visit a specified URL.
