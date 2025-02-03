package users

import (
	"context"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/dogy-app/backend-api/database/repository"
)

type UserRepository struct {
	db *pgxpool.Pool
}

func NewUserRepository(db *pgxpool.Pool) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) GetInternalID(
	ctx context.Context,
	externalId string,
) (uuid.UUID, error) {
	repo := repository.New(r.db)
	internalID, err := repo.GetInternalID(ctx, externalId)
	if err != nil {
		return uuid.UUID{}, err
	}
	return internalID, nil
}

func (r *UserRepository) GetUser(
	ctx context.Context,
	internalID uuid.UUID,
) (CreateUserResponse, error) {
	repo := repository.New(r.db)
	user, err := repo.GetUserByID(ctx, internalID)
	if err != nil {
		return CreateUserResponse{}, err
	}
	return CreateUserResponse{
		ExternalID: user.User.ExternalID,
		CreateUserRequest: CreateUserRequest{
			Name:         user.User.Name,
			Gender:       string(user.User.Gender),
			HasOnboarded: user.User.HasOnboarded,
			Timezone:     user.User.Timezone,
			Notifications: Notifications{
				Enabled:         user.UserNotification.Enabled,
				IsRegistered:    user.UserNotification.IsRegistered,
				DailyEnabled:    user.UserNotification.DailyEnabled,
				PlaytimeEnabled: user.UserNotification.PlaytimeEnabled,
			},
			Subscription: Subscription{
				SubscriptionType: string(user.UserSubscription.SubscriptionType),
				IsTrialMode:      user.UserSubscription.IsTrialMode,
				TrialStartDate:   user.UserSubscription.TrialStartDate.Format("2006-01-02"),
			},
		},
	}, nil
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

func (r *UserRepository) DeleteUser(
	ctx context.Context,
	internalID uuid.UUID,
) error {
	repo := repository.New(r.db)
	err := repo.DeleteUser(ctx, internalID)
	if err != nil {
		return err
	}
	return nil
}
