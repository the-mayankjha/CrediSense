import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import DashboardLayout from "./layouts/DashboardLayout"
import Dashboard from "./pages/Dashboard"
import Assessment from "./pages/Assessment"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="assessment" element={<Assessment />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
