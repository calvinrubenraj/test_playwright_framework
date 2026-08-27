# utils/api_validator.py
from datetime import datetime


class MovieAPIValidator:

    @staticmethod
    def validate_status(response):
        assert response.status == 200, (
            f"Expected status 200 but received {response.status}"
        )

    @staticmethod
    def validate_response_structure(data, category=None):

        assert "page" in data
        assert "results" in data
        assert "total_pages" in data
        assert "total_results" in data
        if category=="newest":
            assert "dates" in data
            assert isinstance(data["dates"], dict)

        assert isinstance(data["page"], int)
        assert isinstance(data["results"], list)
        assert isinstance(data["total_pages"], int)
        assert isinstance(data["total_results"], int)

        assert data["page"] == 1
        assert len(data["results"]) > 0

    @staticmethod
    def validate_movie_schema(movie):

        required_fields = [
            "adult",
            "backdrop_path",
            "genre_ids",
            "id",
            "title",
            "original_language",
            "original_title",
            "overview",
            "popularity",
            "poster_path",
            "release_date",
            "video",
            "vote_average",
            "vote_count",
        ]

        for field in required_fields:
            assert field in movie, (
                f"Required field '{field}' is missing from movie response"
            )

        assert isinstance(movie["adult"], bool)
        assert isinstance(movie["genre_ids"], list)
        assert isinstance(movie["id"], int)
        assert isinstance(movie["title"], str)
        assert isinstance(movie["original_language"], str)
        assert isinstance(movie["overview"], str)
        assert isinstance(movie["popularity"], (int, float))
        assert isinstance(movie["vote_average"], (int, float))
        assert isinstance(movie["vote_count"], int)

    def validate_popularity_descending(api_data: dict):
        results = api_data["results"]

        actual_popularity = [
            movie["popularity"]
            for movie in results
        ]

        expected_popularity = sorted(
            actual_popularity,
            reverse=True
        )

        assert actual_popularity == expected_popularity, (
            f"Movies are not sorted by popularity descending.\n"
            f"Actual:   {actual_popularity}\n"
            f"Expected: {expected_popularity}"
        )

    def validate_release_dates(response_data: dict):

        minimum_date = datetime.strptime(
            response_data["dates"]["minimum"],
            "%Y-%m-%d"
        ).date()

        maximum_date = datetime.strptime(
            response_data["dates"]["maximum"],
            "%Y-%m-%d"
        ).date()

        assert minimum_date <= maximum_date, (
            f"Invalid API date range: "
            f"minimum={minimum_date}, maximum={maximum_date}"
        )

        for movie in response_data["results"]:
            release_date_str = movie.get("release_date")

            assert release_date_str, (
                f"Release date is missing for movie: "
                f"{movie.get('title')}"
            )

            release_date = datetime.strptime(
                release_date_str,
                "%Y-%m-%d"
            ).date()

            assert minimum_date <= release_date <= maximum_date, (
                f"Release date validation failed for "
                f"'{movie['title']}'. "
                f"Release date: {release_date}, "
                f"Expected range: {minimum_date} to {maximum_date}"
            )

    def validate_vote_average_descending(api_data: dict):
        results = api_data["results"]

        actual_vote_average = [
            round(float(movie["vote_average"]), 1)
            for movie in results
        ]

        expected_vote_average = sorted(
            actual_vote_average,
            reverse=True
        )

        assert actual_vote_average == expected_vote_average, (
            f"Movies are not sorted by vote_average descending.\n"
            f"Actual:   {actual_vote_average}\n"
            f"Expected: {expected_vote_average}"
        )
