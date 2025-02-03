package users

type (
	Notifications struct {
		Enabled         bool `json:"enabled"`
		IsRegistered    bool `json:"isRegistered"`
		DailyEnabled    bool `json:"dailyEnabled"`
		PlaytimeEnabled bool `json:"playtimeEnabled"`
	}
	Subscription struct {
		SubscriptionType string `json:"subscriptionType"`
		IsTrialMode      bool   `json:"isTrialMode"`
		TrialStartDate   string `json:"trialStartDate"`
	}
	CreateUserRequest struct {
		Name          string        `json:"name"`
		Gender        string        `json:"gender"`
		HasOnboarded  bool          `json:"hasOnboarded"`
		Timezone      string        `json:"timezone"`
		Notifications Notifications `json:"notifications"`
		Subscription  Subscription  `json:"subscription"`
	}
	CreateUserResponse struct {
		ExternalID string `json:"externalID"`
		CreateUserRequest
	}
)
