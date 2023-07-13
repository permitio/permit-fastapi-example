# How to Implement Authorization in FastAPI

## Introduction
FastAPI exprienced an exponensial growth lately among Python application developers.
It is not only the fastest web framework outhere, but also the clean design for extensibility for needed functionality such as authentication and authorization.
While authentication (verify who the users are) is usually a simple task and solved by using exsiting plugins, authorization (check what users can do and see) is still a grey area for many developers.

In this article, we will go step by step in building an authorization into a FastAPI application.
We will start with the basic principles of building it in FastAPI and continue with fully functional scalable authorization implementation.
By the end of the article, you'll have the whole knowledge you need to implement authorization in your FastAPI application.
Let's dive in!

## The Demo Application
One of the simple ways to demonstrate the various levels of authorization granluarity is a simple todo application.
Let's take a look at the following code that declare a simple todo application with FastAPI.
```python
@app.get("/tasks")
async def get_tasks():
    return tasks

@app.post("/tasks", dependencies=[Depends(authenticate)])
async def create_task(task: Task):
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", dependencies=[Depends(authenticate)])
async def update_task(task_id: int, task: Task):
    tasks[task_id - 1] = task
    return task

@app.delete("/tasks/{task_id}", dependencies=[Depends(authenticate)])
async def delete_task(task_id: int):
    task = tasks[task_id - 1]
    tasks.remove(task)
    return task
```

We also created a mock authentication function so we can make sure all the relevant endpoints are protected and only users with verified identity can access them.
```python
def authenticate(request: Request, token: str = Depends(token_auth_scheme)):
    return verifyToken(token)
```

With this code is mind, let's continue to design the permission model in our application.

## Designing the Authorization Model(s)
Looking at our logic, we can see that we have four endpoints exposes the following operations:
- Get all tasks
- Create a new task
- Update an existing task
- Delete an existing task

Thinking of the permissions required for each operation, we can come up with the following table:
| Operation | Permission |
| --- | --- |
| Get all tasks | Allowed by everyone |
| Create a new task | Allowed only by admin |
| Update an existing task | Allowed by all authenticated users |
| Delete an existing task | Allowed only by admin if the task is marked as done |

If you are familiar with permission models, you can see that we need to support two types of permission models:
- RBAC - Role Based Access Control: To differentiate between admin and regular users.
- ABAC - Attribute Based Access Control: To differentiate between done and not done tasks.

As we have all the code needed to run the logic and authenticate users, let's continue by the idea of implementing those two permission models into our FastAPI application.

## The Authorization Anti-Pattern
One of the approaches to implement authorization in FastAPI is mixing the policy and permissions with the application logic.
For example, we can see developers that create middlewares to the endpoint that check for the relevant permissions in imperative code statements.
Here's an example of such permissions check for the delete endpoint in our demo application:
```python
def allowed_to_delete_task(task_id: int, user: User):
    task = tasks[task_id - 1]
    return task.done or user.is_admin
```

As you can see, this code is failry simple and implement the permissions we defined in the previous section.
Although this code is simple and this overall approach is very common and easy to implement, it has some drawbacks:
- When we need to perform changes on the model, for example allow users perform operations on their own tasks, we need to change the code in the application logic.
- As we create a logic that is specific to the endpoint, we need to dirt our code with multiple authorization function.
- If something is changed in the application itself, for example the task object, we need to rethink the code and change it accordingly.

Let's continue by thinking of a better way to implement authorization in FastAPI.

## The Authorization Service
The main abstract idea of an authorization service is to decouple the policy and permissions from the application logic.
If you think of the previous anti-pattern, we can see that the code we wrote is explicitly declare the policy we have for the particular operation.
In the authorization service approach, we want to create a generic enforcement point in the application that outsource the policy decleration to an external service.

By using such authorization service, we can simplify the implmenentation of our API authorization endpoint to the following code:
```python
def authorize(request: Request, token: str = Depends(token_auth_scheme)):
    action = request.method.lower()
    if action == "get":
        resource = request.path_params
    else:
        resource = request.body

    return authorize_request(token, action, resource)
```

As you can see, the code is very generic and can be used by any application for any endpoint.
Not only that, assuming that we have clean implementation of the `authorize_request` function, we can seamlesly use it even inside an endpoint function.
If for example the endpoint scope has not enough information to authorize the request, we can call the `authorize_request` function everywhere else and get the authorization result.
Let's continue by thinking of the right way to implement the `authorize_request` function.

## Configure our Permissions in Permit.io
As you might think of build this authorization service by yourself, there is a simpler way to do it. Use an authorization as a service provider, Permit.io.
In the following steps, we will configure all the required permissions for our demo application in few easy steps.

1. Create a new (and free!) account in [Permit.io](https://app.permit.io).
2. Configure our application roles:
    - Go to the `Roles` tab and create two roles: `admin` and `user`. TBD - add screenshot of the roles screen
    - Go to the `Users` tab and create a new user with the `admin` role. TBD - add screenshot of the users screen
3. Configure our application permissions:
    - Go to `Policy` screen and click the `Create` -> `Create Resource` button. TBD - add screenshot of the policy screen with the create button
    - Create a new resource with the following details: TBD screenshot of create resource
        - Name: `task`
        - Type: `task`
        - Actions: `get`, `post`, `put`, `delete`
    - In the Policy table, configure the following permissions:
        TBD - add screenshot of the policy screen

As you might paid attention, at this phase we configured only the RBAC permissions of our application and every admin user can delete any task.
Later in this article, we will demonstrate how to scale the permission model of this app with our requirements without changing any application code.
Let's continue with adding the `authorize_request` abstract function in the form of `permit.check` in our FastAPI application.

## Implementing Permit.io in FastAPI
To make everything simpler, we already created a FastAPI application that is ready to use.
Let's continue by doing it interactively in your local Python environment.

First, let's clone the application to your local environment:
```bash
git clone TBD
```

In the cloned repositories, you'll notice the following files:
- `app.py`: The FastAPI application - include the endpoints and the auth functions.
- `requirements.txt`: The required python packages.
- `app_test.py`: A simple test for the application (we will not use it in the article, but it can give you an idea how to test your app authorization).

Looking at the top of the `app.py` file, you'll notice the following code:
```python
async def authorize(request: Request, token: str = Depends(token_auth_scheme), body={}):
    resource_name = request.url.path.split("/")[-1]
    method = request.method.lower()
    resource = await request.json() if method in ["post", "put"] else body
    user = token.credentials

    return await permit.check(user, method, {
        "type": resource_name,
        "attributes": resource
    })
```
As we described before, this is the code that is responsible for the authorization and it's only enforce the decision of the authorization service.

Let's run the application and see how it works:
```bash
uvicorn main:app --reload
```

At this point, you can see our authorization testing in the following video, 

TBD add video

Or, do it yourself by running the following commands in a different terminal:

```bash
curl -X GET http://localhost:8000/tasks
```

As you can see, here are all the mocked tasks that we created on the application startup.

If we try now to create a new task, we'll get an error:

```bash
curl -X POST http://localhost:8000/tasks -d '{"title": "New Task", "description": "New Task Description"}'
```

This error, is because the authentication phase, as we didn't provide any token.
In our application, we mock the token as the email of the user, let's try to create a new task with the admin user:

```bash
curl -X POST http://localhost:8000/tasks -d '{"title": "New Task", "description": "New Task Description"}' -H "Authorization: admin@demo" TBD change user
```

As you can see, we got a new task created.

Let's try now to call the update endpoint, but now with the regular user:

```bash
curl -X PUT TBD code
```

And yay, all our permissions works as expected, regular users are allowed to update tasks.

## Change Permissions with no Code Changes
The most powerful capability we have in this way of implementing authorization is the ability to change the policy without changing the application code.
We are not only able to change the roles or redfine them, we could even add support in new permission models.
For example, as we describe before, our `delete` endpoint authorization has some more requirement than simple RBAC check, we want to verify users can delete only their own tasks after they marked them as done.

Let's add this configuration in Permit app:
1. In the policy page, click on `Create` button and then `Resource Set`.
2. In the `Resource Set` dialog, fill the following details:
    - Name: `Owned and Checked Tasks`
    - Description: `Task resource`
    TBD conditions and screenshot
3. In the Policy table, configure the following permissions:
    TBD screenshot of the policy screen

In this simple configuration, we added a new set of tasks that are owned by the user and marked as done.
Let's continue by allow our users to delete only this resource set by checking the relevant checkbox in the `Policy` page.
TBD add screenshot

_Note: To evaluate the ABAC policy in Permit.io, you should run the [PDP service locally TBD proper link](docs.permit.io). Running decision engine locally will also hlep you to get decision in better performance._

Let's try now to delete a non-owned task:
```bash
curl -X DELETE TBD code
```
As you can see, we got an error, as we just configured users are not allowed to delete tasks that are not theirs.

Trying to delete a task that is owned by the user, but marked as done, succeed!
```bash
curl -X DELETE TBD code
```

Now, think of the time and effort you'll need to implement this change in your application with the traditional approach.
Cool, right?

## Conclusion
In this tutorial, we learned how to implement authorization in FastAPI application using Permit.io.
We learned how to implement the authorization service and how to configure it to support our application permissions.
We also learned how to use the authorization service in our application and how to change the permissions without changing the code.

As the next step, we invite you to excel your authorization knowledge by browsing some other resources in Permit.io blog.
You could also join our authorization Slack community to discuss idea and get advice for the right model for your application.
