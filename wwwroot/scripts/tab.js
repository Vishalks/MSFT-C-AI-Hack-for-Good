
//initialize microsoftTeams in _Layout page
microsoftTeams.initialize();

let saveRed = () => {
    microsoftTeams.settings.registerOnSaveHandler((saveEvent) => {
        microsoftTeams.settings.setSettings({
            websiteUrl: "https://intern-b9eea.azurewebsites.net/",
            contentUrl: "https://intern-b9eea.azurewebsites.net/",
            entityId: "redIconTab",
            suggestedDisplayName: "Vidify",
        });
        saveEvent.notifySuccess();
    });
    document.getElementById('disappear').innerHTML = 'Welcome to Vidify - Making distant learning less distant.';
}
microsoftTeams.settings.setValidityState(true);
saveRed();