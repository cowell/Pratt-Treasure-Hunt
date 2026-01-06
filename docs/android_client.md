# Android client quickstart

This guide walks through creating a simple Android client in Android Studio that talks to the Pratt Treasure Hunt FastAPI backend.

## 1) Create a new project
1. Open **Android Studio** → **New Project** → **Empty Activity**.
2. Choose **Kotlin** as the language, **Minimum SDK** API 26+.

## 2) Add dependencies (app/build.gradle.kts)
```kotlin
dependencies {
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-moshi:2.11.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.8.7")
}
```

## 3) Point the app at your backend
Set your backend base URL. For local emulators, FastAPI at `localhost:8000` is reachable via `http://10.0.2.2:8000`.

```kotlin
private const val BASE_URL = "http://10.0.2.2:8000/"
```

## 4) Define models (Kotlin data classes)
```kotlin
data class User(val id: Int? = null, val email: String, val display_name: String)
data class Hunt(val id: Int? = null, val title: String, val description: String, val reward: String, val active: Boolean)
data class Clue(val id: Int? = null, val hunt_id: Int, val prompt: String, val answer: String, val order: Int)
data class Find(val id: Int? = null, val user_id: Int, val clue_id: Int, val submitted_answer: String, val correct: Boolean = false)
data class LeaderboardRow(val user_id: Int, val score: Int)
data class LeaderboardResponse(val hunt_id: Int, val title: String, val leaderboard: List<LeaderboardRow>)
```

## 5) Create a Retrofit service
```kotlin
interface TreasureHuntApi {
    @POST("users")
    suspend fun createUser(@Body user: User): User

    @POST("hunts")
    suspend fun createHunt(@Body hunt: Hunt): Hunt

    @POST("clues")
    suspend fun createClue(@Body clue: Clue): Clue

    @POST("finds")
    suspend fun submitFind(@Body find: Find): Find

    @GET("hunts/{id}/leaderboard")
    suspend fun getLeaderboard(@Path("id") huntId: Int): LeaderboardResponse
}

private val client = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
    .build()

val api: TreasureHuntApi = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .client(client)
    .addConverterFactory(MoshiConverterFactory.create())
    .build()
    .create(TreasureHuntApi::class.java)
```

## 6) Call the API from a ViewModel
```kotlin
class LeaderboardViewModel : ViewModel() {
    private val _rows = MutableLiveData<List<LeaderboardRow>>()
    val rows: LiveData<List<LeaderboardRow>> = _rows

    fun loadLeaderboard(huntId: Int) {
        viewModelScope.launch {
            runCatching { api.getLeaderboard(huntId) }
                .onSuccess { _rows.value = it.leaderboard }
                .onFailure { /* TODO: show error state */ }
        }
    }
}
```

## 7) Wire it to UI
- In your Activity/Fragment, observe `rows` and render a `RecyclerView`.
- Trigger `loadLeaderboard(huntId)` when the screen opens or after a submission.

## 8) Test with the backend
1. Start the FastAPI server locally: `uvicorn server.main:app --reload`.
2. Run the Android app on the emulator.
3. Create a user, submit a find, and verify the leaderboard updates without duplicate scores.

## Notes
- To test against a remote server, swap `BASE_URL` to your deployed API.
- If you protect the API with auth later, add an `Interceptor` that injects tokens into the `Authorization` header.
