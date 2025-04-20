use super::Error as DailyChallengeError;
use crate::Error::DailyChallenge as Error;
use crate::Result;
use sqlx::{query_as, Executor, Postgres};
use uuid::Uuid;

// Database
pub async fn retrieve_timezone_from_user<'e, E>(conn: E, user_id: Uuid) -> Result<String>
where
    E: Executor<'e, Database = Postgres>,
{
    let timezone: (String,) = query_as("SELECT timezone FROM users WHERE id = $1;")
        .bind(user_id)
        .fetch_one(conn)
        .await
        .map_err(super::Error::from)?;

    if timezone.0.is_empty() {
        return Err(Error(DailyChallengeError::MissingTimezoneForUser));
    }

    Ok(timezone.0)
}

pub async fn retrieve_past_challenges<'e, E>(conn: E, user_id: Uuid) -> Result<Vec<String>>
where
    E: Executor<'e, Database = Postgres>,
{
    let past_challenges: Vec<(String,)> = query_as(
        r#"
        SELECT challenge
        FROM daily_challenges
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 7;
    "#,
    )
    .bind(user_id)
    .fetch_all(conn)
    .await
    .map_err(super::Error::from)?;

    Ok(past_challenges.into_iter().map(|(c,)| c).collect())
}

// AI-related
pub static DAILY_CHALLENGE_PROMPT: &str = r#"
Create daily challenges and dog facts for dog owners. Challenges focus on activities such as learning a new trick, discovering a food recipe, or understanding dog behaviors.

# Steps
1. Identify Challenge Type: Determine whether the daily challenge will be a trick, recipe, behavior insight, or dog fact.
2. Craft a Challenge or Fact: Depending on the type, create a specific, actionable challenge or provide a fascinating, relevant dog fact.
    - For Tricks: Describe a step-by-step process to teach a new trick to a dog.
    - For Recipes: Offer a simple recipe that is healthy and suitable for dogs.
    - For Behaviors: Provide an informative piece about a specific dog behavior and how to positively address or encourage it.
    - For Dog Facts: Present a short, interesting fact about dogs that can intrigue or educate dog owners.
3. Ensure Variety: Rotate through different challenge types and facts to keep the daily content varied and engaging.

# Output Format
Each challenge or fact should be presented in a brief paragraph, clearly stating the type and giving detailed instructions, information, or an intriguing fact relevant to the challenge.

## Examples

### Example 1
- Type: Trick
- Challenge: Teach your dog the 'Shake Hands' trick. Start by getting them to sit, then hold a treat in your hand close to their nose. Tap their paw gently while saying 'shake.' When they lift their paw, praise them and give them the treat. Practice this a few times for them to learn.

### Example 2
- Type: Recipe
- Challenge: Create a simple dog treat using peanut butter and pumpkin puree. Mix 1 cup of pumpkin puree with 1/4 cup of natural peanut butter. Roll the mixture into small balls and place them on a baking sheet. Freeze for a quick and easy dog snack.

### Example 3
- Type: Behavior
- Challenge: Understand your dog's wagging tail. A wagging tail can indicate happiness, but the speed and direction of the wag can signify other emotions like anxiety or excitement. Observe your dog's wagging patterns to better understand their feelings.

### Example 4
- Type: Fact
- Fact: Dogs have three eyelids, an upper lid, a lower lid, and a third lid, known as a nictitating membrane or haw, which helps keep the eye moist and protected.

# Notes
- Customize challenges based on common dog breeds and their attributes for increased relevance.
- Pay attention to seasonal changes, ensuring that challenges are practical and safe for the current weather.
- Ensure recipes use dog-safe ingredients only.
- Dog facts should aim to be surprising or educational."#;

pub static PET_INFO_PROMPT: &str = r#"
Here are the details about my pet. Use this information to create a personalized daily challenge or
dog fact for me."#;

pub static EXCLUDE_PAST_CHALLENGES_PROMPT: &str = r#"
Exclude generating these past challenges. Be sure to generate a unique challenge for today.
Here are the past challenges I have received: "#;
