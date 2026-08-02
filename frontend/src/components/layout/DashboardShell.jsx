import Sidebar from "./Sidebar.jsx";
import MobileTopbar from "./MobileTopbar.jsx";

export default function DashboardShell({ children }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <MobileTopbar />
        {children}
      </div>
    </div>
  );
}
