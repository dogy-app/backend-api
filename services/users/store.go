package users

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/dogy-app/backend-api/database/repository"
)

type UserRepository struct {
	db *pgxpool.Pool
}

func NewUserRepository(db *pgxpool.Pool) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) CreateUser(
	ctx context.Context,
	user *CreateUserRequest,
	externalId string,
) (CreateUserResponse, error) {
	tx, _ := r.db.Begin(ctx)
	defer tx.Rollback(ctx)

	repo := repository.New(tx)
	userBase, err := repo.CreateBaseUser(ctx, repository.CreateBaseUserParams{
		Name:         user.Name,
		Gender:       repository.Gender(user.Gender),
		Timezone:     user.Timezone,
		HasOnboarded: user.HasOnboarded,
		ExternalID:   externalId,
	})
	if err != nil {
		return CreateUserResponse{}, err
	}

	date, err := time.Parse("2006-01-02", user.Subscription.TrialStartDate)
	if err != nil {
		return CreateUserResponse{}, fmt.Errorf("failed to parse date: %w", err)
	}

	userSubscription, err := repo.CreateUserSubscription(
		ctx,
		repository.CreateUserSubscriptionParams{
			UserID:           userBase.ID,
			IsTrialMode:      user.Subscription.IsTrialMode,
			TrialStartDate:   date,
			SubscriptionType: repository.SubscriptionType(user.Subscription.SubscriptionType),
		},
	)
	if err != nil {
		return CreateUserResponse{}, err
	}

	userNotifications, err := repo.CreateUserNotifications(
		ctx,
		repository.CreateUserNotificationsParams{
			UserID:          userBase.ID,
			IsRegistered:    user.Notifications.IsRegistered,
			Enabled:         user.Notifications.Enabled,
			DailyEnabled:    user.Notifications.DailyEnabled,
			PlaytimeEnabled: user.Notifications.PlaytimeEnabled,
		},
	)
	if err != nil {
		return CreateUserResponse{}, err
	}

	if err = tx.Commit(ctx); err != nil {
		return CreateUserResponse{}, err
	}

	return CreateUserResponse{
		ExternalID: userBase.ExternalID,
		CreateUserRequest: CreateUserRequest{
			Name:         userBase.Name,
			Gender:       string(userBase.Gender),
			HasOnboarded: userBase.HasOnboarded,
			Timezone:     userBase.Timezone,
			Notifications: Notifications{
				Enabled:         userNotifications.Enabled,
				IsRegistered:    userNotifications.IsRegistered,
				DailyEnabled:    userNotifications.DailyEnabled,
				PlaytimeEnabled: userNotifications.PlaytimeEnabled,
			},
			Subscription: Subscription{
				SubscriptionType: string(userSubscription.SubscriptionType),
				IsTrialMode:      userSubscription.IsTrialMode,
				TrialStartDate:   userSubscription.TrialStartDate.Format("2006-01-02"),
			},
		},
	}, nil
}
