base_responses = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    422: {"description": "Validation Error"},
    500: {"description": "Internal Server Error"},
}

general_responses = {
    **base_responses,
    200: {
        "content": {"application/json": {"example": {"message": "success"}}},
    },
}

get_token_response = {
    **base_responses,
    200: {
        "content": {
            "application/json": {"example": {"access_token": "string", "token_type": "string"}}
        },
    },
}

single_users_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {"example": {"id": 0, "email": "string", "name": "string"}}
        },
    },
}

all_users_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {"example": [{"id": 0, "email": "string", "name": "string"}]}
        },
    },
}

single_post_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {
                    "id": 0,
                    "title": "string",
                    "post": "string",
                    "date": "string",
                    "user_id": 0,
                }
            }
        },
    },
}

all_posts_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {
                    "total_pages": 0,
                    "total_items": 0,
                    "page_data": {
                        "page_num": 0,
                        "items_count": 0,
                        "items": [
                            {
                                "id": 0,
                                "title": "string",
                                "post": "string",
                                "date": "string",
                                "user_id": 0,
                            }
                        ],
                    },
                }
            }
        },
    },
}
