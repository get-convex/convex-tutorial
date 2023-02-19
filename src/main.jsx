import { StrictMode } from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './Home';
import Login from './Login';
import Map from './Map';
import 'bootstrap/dist/css/bootstrap.min.css';


const address = import.meta.env.VITE_CONVEX_URL;

const convex = new ConvexReactClient(address);

ReactDOM.render(
  <StrictMode>
    <ConvexProvider client={convex}>
      <BrowserRouter>
        <Routes>
          <Route path='' element={<Home />}></Route>
          <Route path='login' element={<Login />}></Route>
          <Route path='login/map' element={<Map />}></Route>
        </Routes>
      </BrowserRouter>
    </ConvexProvider>
  </StrictMode>,
  document.getElementById("root")
);
