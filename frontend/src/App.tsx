import AppContainer from "./containers/AppContainer";
import VideoProvider from "./providers/VideoProvider";

function App() {
  return (
    <VideoProvider>
      <AppContainer />
    </VideoProvider>
  );
}

export default App;
