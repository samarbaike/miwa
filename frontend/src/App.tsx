import { useEffect } from 'react';
import apiClient from './api/client';
import {
  BrowserRouter,
  Routes,
  Route,
  Outlet
} from 'react-router-dom';

import {
  Home,
  Auth,
  Lobby,
  Match,
  Leaderboard,
  Profile,
  NotFound
} from "./pages";

function Layout() {
  useEffect(() => {
    console.log("Initiating health check request via custom apiClient...");

    apiClient<string>('/api/user/me')
      .then((data) => {
        console.log("🟢 Successfully fetched health data from custom client:", data);
        console.log(`${typeof data}`)
      })
      .catch((error) => {
        console.error("🔴 Custom apiClient caught an error:", error);
      });
  }, []);

  return (
    <>
      <Outlet />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/lobby" element={<Lobby />} />
          <Route path="/match/:matchId" element={<Match />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App