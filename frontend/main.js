let inPlayerSearchResView = false

//get html element
const searchObject = document.querySelector('.search-bar')
//event listener that calls function when enter key is pressed
searchObject.addEventListener('keypress', eventSearch)

//define function to happen on submit, e is passed through automatically 
function eventSearch(e){
    if (e.key == 'Enter'){
        //e is event object, e.target is element where event happened (like entire search bar), must get value
        const query = e.target.value.trim()   //trim to remove any leading or ending whitespace
        if (query){
            //fetch request to api
            fetchMatchingNames(query)

        }
    }
}

async function fetchMatchingNames(query){
    //use ?= to adhere to REST query parameter design principles
    // this endpoint is query as it returns a subset or list of matching players, not specific identifier
    apiURL = `http://localhost:8000/search?name=${encodeURIComponent(query)}` //encode name so that url does not break w special chars
    try{
        response = await fetch(apiURL)
        if (response.ok){
            const data = await response.json()
            console.log('API response:', data);
            displayData(data, query)
        }else{
            alert(`No matching players found for: ${query}`)
        }
    }catch (error){
        console.error('Fetch error:', error);
        alert('Error retrieving data')
    }

}

//function that displays data from search bar
function displayData(data, query){
    if (inPlayerSearchResView === false){
        playerSearchResultsView(query)
        inPlayerSearchResView = true
    }

    const results = document.querySelector('#results')
    //clear previous searches
    results.innerHTML = ''

    // Add results header
    const resultsHeader = document.createElement('div')
    resultsHeader.classList.add('results-header')
    resultsHeader.innerHTML = `
        <h2>Search Results for "${query}" (${data.players.length} found)</h2>
    `
    results.appendChild(resultsHeader)

    // Create results container BEFORE the forEach loop
    const resultsContainer = document.createElement('div')
    resultsContainer.classList.add('results-container')

    data.players.forEach(player => {
        //create new player row for each player returned
        const playerRow = document.createElement('div')
        playerRow.classList.add('player-row')

        playerRow.innerHTML = `
            <span class="player-name-link" data-player-id="${player.id}">${player.first_name} ${player.last_name}</span>
            <span class="player-team">${player.team_name}</span>
            <span class="player-position">${player.position}</span>
        `
        
        // Add click handler to just the name
        const nameLink = playerRow.querySelector('.player-name-link')
        nameLink.addEventListener('click', () => {
            goToPlayerPage(player.id)
        })
        
        //append player row to results container
        resultsContainer.appendChild(playerRow)
    });

    results.appendChild(resultsContainer)
    
}

function playerSearchResultsView(query){
    const searchContainer = document.querySelector('.search-container')
    const searchHeading = document.querySelector('.search-heading')
    
    // Move search container to top and make it smaller
    searchContainer.style.marginTop = '20px'
    searchContainer.style.marginBottom = '30px'
    
    // Update heading
    if (searchHeading) {
        searchHeading.textContent = 'FPL Player Search'
        searchHeading.style.fontSize = '1.5em'
        searchHeading.style.marginBottom = '15px'
    }
    
    // Make search bar smaller
    const searchBar = document.querySelector('.search-bar')
    searchBar.style.width = '40%'
    searchBar.style.fontSize = '1em'
}

//player profile page function
async function goToPlayerPage(id){
    url = `http://localhost:8000/profile/${id}`

    try{
        response = await fetch(url)
        if (response.ok){
            const data = await response.json()
            console.log('API response:', data);
            playerProfilePage(data, id)
        }else{
            alert('Response code error')
        }
    }catch (error){
        console.error('Fetch error:', error);
        alert('Error retrieving data')
    }
}

function playerProfilePage(data, id){
    //transition to player profile page structure
    const results = document.querySelector('#results')
    if(results) results.remove()

    const search = document.querySelector('.search-container')
    if(search) search.remove()

    const profDiv = document.querySelector('#player-profile')
    profDiv.innerHTML = '' // Clear any existing content

    // Add back button
    const backButton = document.createElement('button')
    backButton.classList.add('back-button')
    backButton.textContent = 'Back to Search'
    backButton.addEventListener('click', () => {
        location.reload() // Simple way to go back to search
    })
    profDiv.appendChild(backButton)

    //header
    const profHeader = document.createElement('div')
    profHeader.classList.add('prof-header')
    profHeader.innerHTML = `
        <h2>${data.first_name} ${data.last_name}</h2>
        <p>Comprehensive player statistics and performance data. Select a season below to view detailed metrics and match-by-match analysis.</p>
    `
    profDiv.appendChild(profHeader)

    // Enhanced body with cards
    const profBody = document.createElement('div')
    profBody.classList.add('prof-body')
    
    // Basic info cards
    const basicInfoCard = document.createElement('div')
    basicInfoCard.classList.add('info-card')
    basicInfoCard.innerHTML = `
        <h3>Player Information</h3>
        <p><span class="highlight">${data.first_name} ${data.last_name}</span></p>
        <p>Position: <span class="highlight">${data.curr_position}</span></p>
        <p>Current Team: <span class="highlight">${data.current_team}</span></p>
    `
    
    const careerCard = document.createElement('div')
    careerCard.classList.add('info-card')
    const earliestSeason = data.all_seasons[data.all_seasons.length-1]
    let status = "Not Active"
    if(data.all_seasons[0] == "2024-25"){
        status = "Active"
    }
    careerCard.innerHTML = `
        <h3>Career Overview</h3>
        <p>Seasons Available: <span class="highlight">${data.all_seasons ? data.all_seasons.length : 'N/A'}</span></p>
        <p>Status: <span class="highlight">${status} Player</span></p>
        <p>Data Since: <span class="highlight">${earliestSeason} Season</span></p>
    `

    profBody.appendChild(basicInfoCard)
    profBody.appendChild(careerCard)
    profDiv.appendChild(profBody)

    // Season selector section
    const seasonSelector = document.createElement('div')
    seasonSelector.classList.add('season-selector')
    
    let seasonOptions = '<option value="">Select a season for detailed stats</option>'
    if(data.all_seasons && data.all_seasons.length > 0) {
        data.all_seasons.forEach(season => {
            seasonOptions += `<option value="${season}">${season}</option>`
        })
    } else {
        // Placeholder seasons if none provided
        const seasons = ['2023/24', '2022/23', '2021/22', '2020/21', '2019/20']
        seasons.forEach(season => {
            seasonOptions += `<option value="${season}">${season}</option>`
        })
    }
    
    seasonSelector.innerHTML = `
        <h3>Season Analysis</h3>
        <div class="dropdown-container">
            <select class="season-dropdown" id="season-select">
                ${seasonOptions}
            </select>
        </div>
        <p style="color: rgba(255,255,255,0.8); margin-top: 10px;">Choose a season to view goals, assists, clean sheets, and match performance</p>
    `
    profDiv.appendChild(seasonSelector)

    // Coming soon section
    const comingSoon = document.createElement('div')
    comingSoon.classList.add('coming-soon')
    comingSoon.innerHTML = `
        <h4>Enhanced Features Coming Soon</h4>
        <p>Match-by-match analysis • Performance trends • Head-to-head comparisons • Injury history • Transfer value tracking • Advanced metrics and much more!</p>
    `
    profDiv.appendChild(comingSoon)

    // Add event listener for dropdown
    const seasonSelect = document.getElementById('season-select')
    seasonSelect.addEventListener('change', (e) => {
        if(e.target.value) { 
            console.log(e.target.value)
            seasonData(id, e.target.value)
        }
    })
}

async function seasonData(id, season){
    url = `http://localhost:8000/profile/${id}/${season}`
    try{
        response = await fetch(url)
        if (response.ok){
            const data = await response.json()
            console.log('API response:', data);
            playerSeasonPage(data)
        }else{
            alert('Response code error')
        }
    }catch (error){
        console.error('Fetch error:', error);
        alert('Error retrieving data')
    }
}

function playerSeasonPage(data){
    //remove all profile page 
    const playerProf = document.querySelector('#player-profile')
    playerProf.remove()

    const seasonDiv = document.querySelector('#player-season-page')
    seasonDiv.innerHTML = ''


    // Add back button to go back to search
    const backButton = document.createElement('button')
    backButton.classList.add('back-button')
    backButton.textContent = 'Back to Search'
    backButton.addEventListener('click', () => {
        location.reload()
    })
    seasonDiv.appendChild(backButton)

    //header
    const seasonHeader = document.createElement('div')
    seasonHeader.classList.add('season-header')
    seasonHeader.innerHTML = `
        <h2>${data.endOfSeason.first_name} ${data.endOfSeason.last_name}</h2>
        <p>Stats for ${data.endOfSeason.season} season.</p>
    `
    seasonDiv.appendChild(seasonHeader)

    /*note: cost not available due to not using correct name when collecting data into database.
     shouldve used row.get('cost_change_start') but used just 'cost'. so everyones cost is -1 or default val*/
    const eosHeader = document.createElement('div')
    eosHeader.classList.add('gw-header')
    eosHeader.innerHTML = `
        <h2>End of Season Stats for ${data.endOfSeason.season}</h2>
    `
    seasonDiv.appendChild(eosHeader)

    const eosTableContainer = document.createElement('div')
    eosTableContainer.classList.add('eos-table-container')
    const eosTable = document.createElement('div')
    eosTable.classList.add('eos-table')
    eosTable.innerHTML = `
        <table>
            <thead>
                <tr>
                <th>Goals Scored</th>
                <th>Assists</th>
                <th>Minutes</th>
                <th>Total Points</th>
                <th>Selected By Percent</th>
                <th>Selected Rank</th>
                <th>Bonus</th>
                <th>Creativity</th>
                <th>Creativity Rank</th>
                <th>Expected Assists</th>
                <th>Expected Assists Per 90</th>
                <th>Expected Goal Involvements</th>
                <th>Expected Goal Involvements Per 90</th>
                <th>Expected Goals</th>
                <th>Expected Goals Per 90</th>
                <th>Expected Goals Conceded</th>
                <th>Expected Goals Conceded Per 90</th>
                <th>Fpl Season Id</th>
                <th>Ict Index</th>
                <th>Influence</th>
                <th>Own Goals</th>
                <th>Penalties Missed</th>
                <th>Penalties Order</th>
                <th>Penalties Saved</th>
                <th>Points Per Game</th>
                <th>Points Per Game Rank</th>
                <th>Saves</th>
                <th>Saves Per 90</th>
                <th>Starts</th>
                <th>Starts Per 90</th>
                <th>Team Name</th>
                <th>Threat</th>
                <th>Transfers In</th>
                <th>Transfers Out</th>
                <th>Yellow Cards</th>
                <th>Red Cards</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                <td>${data.endOfSeason.goals_scored}</td>
                <td>${data.endOfSeason.assists}</td>
                <td>${data.endOfSeason.minutes}</td>
                <td>${data.endOfSeason.total_points}</td>
                <td>${data.endOfSeason.selected_by_percent}</td>
                <td>${data.endOfSeason.selected_rank}</td>
                <td>${data.endOfSeason.bonus}</td>
                <td>${data.endOfSeason.creativity}</td>
                <td>${data.endOfSeason.creativity_rank}</td>
                <td>${data.endOfSeason.expected_assists}</td>
                <td>${data.endOfSeason.expected_assists_per_90}</td>
                <td>${data.endOfSeason.expected_goal_involvements}</td>
                <td>${data.endOfSeason.expected_goal_involvements_per_90}</td>
                <td>${data.endOfSeason.expected_goals}</td>
                <td>${data.endOfSeason.expected_goals_per_90}</td>
                <td>${data.endOfSeason.expected_goals_conceded}</td>
                <td>${data.endOfSeason.expected_goals_conceded_per_90}</td>
                <td>${data.endOfSeason.fpl_season_id}</td>
                <td>${data.endOfSeason.ict_index}</td>
                <td>${data.endOfSeason.influence}</td>
                <td>${data.endOfSeason.own_goals}</td>
                <td>${data.endOfSeason.penalties_missed}</td>
                <td>${data.endOfSeason.penalties_order}</td>
                <td>${data.endOfSeason.penalties_saved}</td>
                <td>${data.endOfSeason.points_per_game}</td>
                <td>${data.endOfSeason.points_per_game_rank}</td>
                <td>${data.endOfSeason.saves}</td>
                <td>${data.endOfSeason.saves_per_90}</td>
                <td>${data.endOfSeason.starts}</td>
                <td>${data.endOfSeason.starts_per_90}</td>
                <td>${data.endOfSeason.team_name}</td>
                <td>${data.endOfSeason.threat}</td>
                <td>${data.endOfSeason.transfers_in}</td>
                <td>${data.endOfSeason.transfers_out}</td>
                <td>${data.endOfSeason.yellow_cards}</td>
                <td>${data.endOfSeason.red_cards}</td>
                </tr>
            </tbody>
        </table>
    `

    eosTableContainer.appendChild(eosTable)
    seasonDiv.appendChild(eosTableContainer)

    const gwHeader = document.createElement('div')
    gwHeader.classList.add('gw-header')
    gwHeader.innerHTML = `
        <h2>Gameweek by Gameweek Stats for ${data.endOfSeason.season}</h2>
    `
    seasonDiv.appendChild(gwHeader)

    const gwTableContainer = document.createElement('div')
    gwTableContainer.classList.add('eos-table-container')

    const gwTable = document.createElement('div')
    gwTable.classList.add('eos-table')
    gwTable.innerHTML = `
        <table>
            <thead>
                <tr>
                <th>Gameweek</th>
                <th>Opponent</th>
                <th>Total Points</th>
                <th>Goals Scored</th>
                <th>Assists</th>
                <th>Minutes</th>
                <th>Selected By</th>
                <th>Home or Away</th>
                <th>Away Score</th>
                <th>Home Score</th>
                <th>Clean Sheets</th>
                <th>Bonus</th>
                <th>Creativity</th>
                <th>Expected Assists</th>
                <th>Expected Goal Involvements</th>
                <th>Expected Goals</th>
                <th>Expected Goals Conceded</th>
                <th>Ict Index</th>
                <th>Influence</th>
                <th>Own Goals</th>
                <th>Penalties Missed</th>
                <th>Penalties Saved</th>
                <th>Saves</th>
                <th>Starts</th>
                <th>Threat</th>
                <th>Transfers In</th>
                <th>Transfers Out</th>
                <th>Yellow Cards</th>
                <th>Red Cards</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    `
    const table = gwTable.querySelector('tbody')
    // Iterate over each gameweek
    data.gameweekStats.forEach((gw) => {
        const row = document.createElement('tr')
        row.innerHTML = `
            <td>${gw.gameweek}</td>
            <td>${gw.opponent_name}</td>
            <td>${gw.round_points}</td>
            <td>${gw.goals_scored}</td>
            <td>${gw.assists}</td>
            <td>${gw.minutes}</td>
            <td>${gw.selected}</td>
            <td>${gw.was_home}</td>
            <td>${gw.team_away_score}</td>
            <td>${gw.team_home_score}</td>
            <td>${gw.clean_sheets}</td>
            <td>${gw.bonus}</td>
            <td>${gw.creativity}</td>
            <td>${gw.expected_assists}</td>
            <td>${gw.expected_goal_involvements}</td>
            <td>${gw.expected_goals}</td>
            <td>${gw.expected_goals_conceded}</td>
            <td>${gw.ict_index}</td>
            <td>${gw.influence}</td>
            <td>${gw.own_goals}</td>
            <td>${gw.penalties_missed}</td>
            <td>${gw.penalties_saved}</td>
            <td>${gw.saves}</td>
            <td>${gw.starts}</td>
            <td>${gw.threat}</td>
            <td>${gw.transfers_in}</td>
            <td>${gw.transfers_out}</td>
            <td>${gw.yellow_cards}</td>
            <td>${gw.red_cards}</td>
        `
        table.appendChild(row)
    })

    gwTableContainer.appendChild(gwTable)
    seasonDiv.appendChild(gwTableContainer)

}

