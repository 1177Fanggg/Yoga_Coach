import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LivePracticePage from './pages/LivePracticePage';
import HistoryPage from './pages/HistoryPage';
import SessionDetailPage from './pages/SessionDetailPage';

const router = createBrowserRouter([
    {
        path: '/',
        element: <LivePracticePage />,
    },
    {
        path: '/history',
        element: <HistoryPage />,
    },
    {
        path: '/session/:sessionId',
        element: <SessionDetailPage />,
    },
]);

const Router = () => {
    return <RouterProvider router={router} />;
};

export default Router;
