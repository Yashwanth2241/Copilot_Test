"""
Tests for Activity Management API endpoints using AAA (Arrange-Act-Assert) pattern
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_dict(self, client, reset_activities):
        # Arrange
        # (activities are reset by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_all_fields(self, client, reset_activities):
        # Arrange
        # (activities are reset by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_shows_correct_participant_count(self, client, reset_activities):
        # Arrange
        # (activities are reset by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 1
        assert len(data["Programming Class"]["participants"]) == 1
        assert len(data["Gym Class"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(reset_activities[activity_name]["participants"]) == initial_count + 1
        assert email in reset_activities[activity_name]["participants"]
    
    def test_signup_duplicate_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student1 in reset_activities[activity_name]["participants"]
        assert student2 in reset_activities[activity_name]["participants"]
    
    def test_signup_same_student_multiple_activities(self, client, reset_activities):
        # Arrange
        email = "multiactivity@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in reset_activities[activity1]["participants"]
        assert email in reset_activities[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in reset_activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in reset_activities[activity_name]["participants"]
    
    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act - Unregister
        response1 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert first response
        assert response1.status_code == 200
        assert email not in reset_activities[activity_name]["participants"]
        
        # Act - Sign up again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert second response
        assert response2.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
    
    def test_unregister_one_of_multiple_participants(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        # Add another participant first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert email_to_remove not in reset_activities[activity_name]["participants"]
        assert "newstudent@mergington.edu" in reset_activities[activity_name]["participants"]
