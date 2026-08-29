# utils/api_validator.py
from datetime import datetime
import traceback

import allure


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

    @staticmethod
    def validate_tv_schema(tv_show):

        required_fields = [
            "adult",
            "backdrop_path",
            "first_air_date",
            "genre_ids",
            "id",
            "name",
            "origin_country",
            "original_language",
            "original_name",
            "overview",
            "popularity",
            "poster_path",
            "softcore",
            "vote_average",
            "vote_count",
        ]

        for field in required_fields:
            assert field in tv_show, (
                f"Required field '{field}' is missing from movie response"
            )

        assert isinstance(tv_show["adult"], bool)
        assert isinstance(tv_show["genre_ids"], list)
        assert isinstance(tv_show["id"], int)
        assert isinstance(tv_show["name"], str)
        assert isinstance(tv_show["original_language"], str)
        assert isinstance(tv_show["overview"], str)
        assert isinstance(tv_show["popularity"], (int, float))
        assert isinstance(tv_show["vote_average"], (int, float))
        assert isinstance(tv_show["vote_count"], int)

    @staticmethod
    def request_payload(response_url):
        payload = response_url.split("?")[1]
        return {payload_raw.split("=")[0]: payload_raw.split("=")[1] for payload_raw in payload.split("&")}

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

    def validate_year_range(response_data: dict, min_year: str, max_year: str):

        for movie in response_data["results"]:
            release_date_str = movie.get("release_date")

            assert release_date_str, (
                f"Release date is missing for movie: "
                f"{movie.get('title')}"
            )

            release_date = int(release_date_str.split("-")[0])

            try:
                assert int(min_year) <= release_date <= int(max_year), (
                    f"Release date validation failed for "
                    f"'{movie['title']}'. "
                    f"Release date: {release_date}, "
                    f"Expected range: {min_year} to {max_year}"
                )
            except AssertionError as error:
                # 1. Capture the full Python error stack trace
                error_traceback = traceback.format_exc()

                # 2. Attach the error log as plain text to the current Allure subtest
                allure.attach(
                    body=error_traceback,
                    name="Assertion Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 3. Crucial: Re-raise the error so Allure marks this subtest as Failed
                raise error

    def validate_rating_range(response_data: dict, min_rating: str, max_rating: str):

        for movie in response_data["results"]:
            vote_average_str = movie.get("vote_average")

            assert vote_average_str, (
                f"Release date is missing for movie: "
                f"{movie.get('title')}"
            )

            vote_average = int(vote_average_str)

            try:
                assert int(min_rating) <= vote_average <= int(max_rating), (
                    f"Rating validation failed for "
                    f"'{movie['title']}'. "
                    f"Vote average: {vote_average}, "
                    f"Expected range: {min_rating} to {max_rating}"
                )
            except AssertionError as error:
                # 1. Capture the full Python error stack trace
                error_traceback = traceback.format_exc()

                # 2. Attach the error log as plain text to the current Allure subtest
                allure.attach(
                    body=error_traceback,
                    name="Assertion Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 3. Crucial: Re-raise the error so Allure marks this subtest as Failed
                raise error

    def validate_genre_id(response_data: dict, genre_id: str):

        for movie in response_data["results"]:
            genre_id_list = movie.get("genre_ids")

            assert genre_id_list, (
                f"Release date is missing for movie: "
                f"{movie.get('title')}"
            )

            try:
                assert genre_id in genre_id_list, (
                    f"Genre validation failed for "
                    f"'{movie['title']}'. "
                    f" reference genre id: {genre_id}, "
                    f"Card's genre id list: {genre_id_list}"
                )
            except AssertionError as error:
                # 1. Capture the full Python error stack trace
                error_traceback = traceback.format_exc()

                # 2. Attach the error log as plain text to the current Allure subtest
                allure.attach(
                    body=error_traceback,
                    name="Assertion Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 3. Crucial: Re-raise the error so Allure marks this subtest as Failed
                raise error
