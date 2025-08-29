import asyncio
from collections.abc import Awaitable, Callable

from typing import Any

import flet as ft

from app.services.system import get_system_status
from app.services.system.ui import get_status_icon, get_component_label

from .core.theme import ThemeManager


def create_frontend_app() -> Callable[[ft.Page], Awaitable[None]]:
    """Returns the Flet target function - system health dashboard"""

    async def flet_main(page: ft.Page) -> None:
        page.title = "Aegis Stack - System Dashboard"
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO

        # Initialize theme system
        theme_manager = ThemeManager(page)
        await theme_manager.initialize_themes()

        # Theme toggle button
        theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Switch to Dark Mode",
            icon_size=24,
        )

        async def toggle_theme(_: Any) -> None:
            """Toggle theme and update button icon"""
            await theme_manager.toggle_theme()
            # Update button icon based on new theme
            if theme_manager.is_dark_mode:
                theme_button.icon = ft.Icons.LIGHT_MODE
                theme_button.tooltip = "Switch to Light Mode"
            else:
                theme_button.icon = ft.Icons.DARK_MODE
                theme_button.tooltip = "Switch to Dark Mode"
            page.update()

        theme_button.on_click = toggle_theme

        # Dashboard header with theme switch
        header = ft.Container(
            content=ft.Row(
                [
                    # Left side - title and subtitle
                    ft.Column(
                        [
                            ft.Text(
                                "🏛️ Aegis Stack",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.PRIMARY,
                            ),
                            ft.Text(
                                "System Health Dashboard",
                                size=18,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                    ),
                    # Center - status summary (will be updated)
                    ft.Container(
                        content=ft.Text(
                            "Loading...", size=16, color=ft.Colors.ON_SURFACE
                        ),
                        padding=15,
                        bgcolor=ft.Colors.SURFACE,
                        border_radius=8,
                    ),
                    # Right side - theme toggle
                    ft.Container(
                        content=theme_button,
                        padding=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            margin=ft.margin.only(bottom=30),
        )

        # Create responsive grid layout containers
        # Top row - System metrics
        metrics_row = ft.Container(
            content=ft.Row([], spacing=15),
            margin=ft.margin.only(bottom=20),
        )

        # Middle row - Main components
        components_row = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "🏗️ Infrastructure Components",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PRIMARY,
                    ),
                    ft.Row([], spacing=15, wrap=True),
                ]
            ),
            margin=ft.margin.only(bottom=20),
        )

        # Bottom row - System info and queues
        details_row = ft.Container(
            content=ft.Row([], spacing=15),
            margin=ft.margin.only(bottom=20),
        )

        # Add components to page with new horizontal layout
        page.add(
            header,
            metrics_row,
            components_row,
            details_row,
        )

        async def refresh_status() -> None:
            """Refresh system status data using Material Design color tokens"""
            try:
                status = await get_system_status()

                # Get current theme state directly from page (most reliable)
                is_light_mode = page.theme_mode == ft.ThemeMode.LIGHT

                # Extract aegis component and its sub-components
                aegis_component = None
                if "aegis" in status.components:
                    aegis_component = status.components["aegis"]

                if not aegis_component or not aegis_component.sub_components:
                    return

                components = aegis_component.sub_components

                # Update header status summary
                status_color = (
                    ft.Colors.GREEN if status.overall_healthy else ft.Colors.ERROR
                )
                status_icon = "✅" if status.overall_healthy else "❌"
                status_text = (
                    "System Healthy" if status.overall_healthy else "Issues Detected"
                )

                header.content.controls[1].content = ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(status_icon, size=18),
                                ft.Text(
                                    status_text,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=status_color,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Text(
                            f"{status.health_percentage:.1f}% • "
                            f"{len(status.healthy_components)} healthy",
                            size=12,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Text(
                            f"Updated: {status.timestamp.strftime('%H:%M:%S')}",
                            size=10,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=2,
                )

                # Update header status container background
                header.content.controls[1].bgcolor = ft.Colors.SURFACE

                # Create system metrics cards (horizontal row)
                metrics_cards = []
                backend_component = components.get("backend")
                if backend_component and backend_component.sub_components:
                    for metric_name, metric in backend_component.sub_components.items():
                        if metric.healthy:
                            bg_color = (
                                ft.Colors.GREEN_100
                                if is_light_mode
                                else ft.Colors.GREEN_900
                            )
                            text_color = (
                                ft.Colors.GREEN_800
                                if is_light_mode
                                else ft.Colors.GREEN_100
                            )
                            border_color = ft.Colors.GREEN
                        else:
                            bg_color = (
                                ft.Colors.RED_100
                                if is_light_mode
                                else ft.Colors.RED_900
                            )
                            text_color = (
                                ft.Colors.RED_800
                                if is_light_mode
                                else ft.Colors.RED_100
                            )
                            border_color = ft.Colors.ERROR
                        icon = get_status_icon(metric.status)

                        # Extract percentage from message
                        percentage = "0%"
                        if "%" in metric.message:
                            percentage = metric.message.split(":")[1].strip()

                        metrics_cards.append(
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text(icon, size=14),
                                                ft.Text(
                                                    metric_name.upper(),
                                                    size=12,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=text_color,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                        ft.Text(
                                            percentage,
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=text_color,
                                        ),
                                        ft.Text(
                                            metric.message.split(":")[0],
                                            size=10,
                                            color=text_color,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=4,
                                ),
                                padding=15,
                                bgcolor=bg_color,
                                border=ft.border.all(1, border_color),
                                border_radius=8,
                                width=120,
                                height=100,
                            )
                        )

                metrics_row.content.controls = metrics_cards

                # Create main component cards (horizontal grid)
                component_cards = []

                for comp_name, component in components.items():
                    # Show backend as a component card too, for consistency

                    if component.healthy:
                        bg_color = (
                            ft.Colors.GREEN_100
                            if is_light_mode
                            else ft.Colors.GREEN_900
                        )
                        text_color = (
                            ft.Colors.GREEN_800
                            if is_light_mode
                            else ft.Colors.GREEN_100
                        )
                        border_color = ft.Colors.GREEN
                    else:
                        bg_color = (
                            ft.Colors.RED_100 if is_light_mode else ft.Colors.RED_900
                        )
                        text_color = (
                            ft.Colors.RED_800 if is_light_mode else ft.Colors.RED_100
                        )
                        border_color = ft.Colors.ERROR
                    icon = get_status_icon(component.status)
                    tech_name = get_component_label(comp_name)

                    # Build card content
                    card_content = [
                        ft.Row(
                            [
                                ft.Text(icon, size=16),
                                ft.Column(
                                    [
                                        ft.Text(
                                            comp_name.title(),
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=text_color,
                                        ),
                                        ft.Text(
                                            tech_name,
                                            size=12,
                                            color=text_color,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Text(
                            component.message[:50] + "..."
                            if len(component.message) > 50
                            else component.message,
                            size=11,
                            color=text_color,
                        ),
                    ]

                    # Add database-specific metadata display
                    if comp_name == "database" and component.metadata:
                        db_info = []
                        
                        # Show SQLite version if available
                        if "version" in component.metadata:
                            db_info.append(f"SQLite v{component.metadata['version']}")
                        
                        # Show file size if available
                        if "file_size_human" in component.metadata:
                            size = component.metadata['file_size_human']
                            db_info.append(f"Size: {size}")
                        
                        # Show WAL status if available
                        if "wal_enabled" in component.metadata:
                            wal_enabled = component.metadata["wal_enabled"]
                            wal_status = "WAL" if wal_enabled else "DELETE"
                            db_info.append(f"Mode: {wal_status}")
                        
                        # Show connection pool size if available
                        if "connection_pool_size" in component.metadata:
                            pool_size = component.metadata['connection_pool_size']
                            db_info.append(f"Pool: {pool_size}")
                        
                        # Add database info to card if we have any
                        if db_info:
                            card_content.append(
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Database Info:",
                                                size=10,
                                                weight=ft.FontWeight.BOLD,
                                                color=text_color,
                                            ),
                                            ft.Text(
                                                " • ".join(db_info),
                                                size=10,
                                                color=text_color,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    margin=ft.margin.only(top=8),
                                )
                            )

                    # Add sub-component indicators
                    if component.sub_components:
                        sub_status = []
                        for sub_name, sub_comp in component.sub_components.items():
                            sub_icon = get_status_icon(sub_comp.status)
                            sub_status.append(f"{sub_icon} {sub_name}")

                        if (
                            comp_name == "worker"
                            and "queues" in component.sub_components
                        ):
                            # Special handling for worker queues
                            queues_comp = component.sub_components["queues"]
                            if queues_comp.sub_components:
                                queue_icons = [
                                    get_status_icon(q.status)
                                    for q in queues_comp.sub_components.values()
                                ]
                                card_content.append(
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Text(
                                                    "Queues:",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=text_color,
                                                ),
                                                ft.Text(" ".join(queue_icons), size=12),
                                            ],
                                            spacing=5,
                                        ),
                                        margin=ft.margin.only(top=8),
                                    )
                                )
                        else:
                            # Show sub-components as compact indicators
                            if len(sub_status) <= 3:
                                card_content.append(
                                    ft.Container(
                                        content=ft.Text(
                                            " | ".join(sub_status),
                                            size=10,
                                            color=text_color,
                                        ),
                                        margin=ft.margin.only(top=8),
                                    )
                                )

                    component_cards.append(
                        ft.Container(
                            content=ft.Column(card_content, spacing=8),
                            padding=15,
                            bgcolor=bg_color,
                            border=ft.border.all(1, border_color),
                            border_radius=8,
                            width=240,
                            height=140,
                        )
                    )

                components_row.content.controls[1].controls = component_cards

                # Create bottom row with system info and detailed worker queues
                bottom_cards = []

                # System info card
                info_bg_color = (
                    ft.Colors.BLUE_100 if is_light_mode else ft.Colors.BLUE_900
                )
                info_text_color = (
                    ft.Colors.BLUE_800 if is_light_mode else ft.Colors.BLUE_100
                )

                sys_info_content = [
                    ft.Text(
                        "System Info",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=info_text_color,
                    )
                ]
                if status.system_info:
                    for key, value in status.system_info.items():
                        sys_info_content.append(
                            ft.Text(
                                f"{key.replace('_', ' ').title()}: {value}",
                                size=11,
                                color=info_text_color,
                            )
                        )

                bottom_cards.append(
                    ft.Container(
                        content=ft.Column(sys_info_content, spacing=4),
                        padding=15,
                        bgcolor=info_bg_color,
                        border=ft.border.all(1, ft.Colors.PRIMARY),
                        border_radius=8,
                        width=300,
                    )
                )

                # Worker queues detailed card
                worker_comp = components.get("worker")
                if (
                    worker_comp
                    and worker_comp.sub_components
                    and "queues" in worker_comp.sub_components
                ):
                    queues_comp = worker_comp.sub_components["queues"]
                    queue_bg_color = (
                        ft.Colors.PURPLE_100 if is_light_mode else ft.Colors.PURPLE_900
                    )
                    queue_text_color = (
                        ft.Colors.PURPLE_800 if is_light_mode else ft.Colors.PURPLE_100
                    )

                    queue_content = [
                        ft.Text(
                            "Worker Queues",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=queue_text_color,
                        )
                    ]

                    if queues_comp.sub_components:
                        for queue_name, queue in queues_comp.sub_components.items():
                            icon = get_status_icon(queue.status)
                            # Extract job count from message
                            job_info = ""
                            if "completed" in queue.message:
                                job_info = queue.message.split(":")[-1].strip()

                            queue_content.append(
                                ft.Row(
                                    [
                                        ft.Text(icon, size=12),
                                        ft.Text(
                                            queue_name,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=queue_text_color,
                                        ),
                                        ft.Text(
                                            job_info, size=10, color=queue_text_color
                                        ),
                                    ],
                                    spacing=8,
                                )
                            )

                    bottom_cards.append(
                        ft.Container(
                            content=ft.Column(queue_content, spacing=6),
                            padding=15,
                            bgcolor=queue_bg_color,
                            border=ft.border.all(1, ft.Colors.PURPLE),
                            border_radius=8,
                            width=300,
                        )
                    )

                # Database details card (if database component exists)
                database_comp = components.get("database")
                if database_comp and database_comp.metadata:
                    db_bg_color = (
                        ft.Colors.CYAN_100 if is_light_mode else ft.Colors.CYAN_900
                    )
                    db_text_color = (
                        ft.Colors.CYAN_800 if is_light_mode else ft.Colors.CYAN_100
                    )

                    db_content = [
                        ft.Text(
                            "Database Details",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=db_text_color,
                        )
                    ]

                    # Show detailed database metadata
                    metadata = database_comp.metadata
                    
                    # Version and implementation
                    if "version" in metadata and "implementation" in metadata:
                        db_content.append(
                            ft.Text(
                                f"{metadata['implementation'].upper()} "
                                f"v{metadata['version']}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=db_text_color,
                            )
                        )
                    
                    # File info
                    if "file_size_human" in metadata and "file_size_bytes" in metadata:
                        db_content.append(
                            ft.Text(
                                f"File Size: {metadata['file_size_human']} "
                                f"({metadata['file_size_bytes']:,} bytes)",
                                size=11,
                                color=db_text_color,
                            )
                        )
                    
                    # Connection info
                    if "connection_pool_size" in metadata:
                        db_content.append(
                            ft.Text(
                                f"Connection Pool: "
                                f"{metadata['connection_pool_size']} connections",
                                size=11,
                                color=db_text_color,
                            )
                        )
                    
                    # SQLite PRAGMA settings
                    if "pragma_settings" in metadata:
                        pragma = metadata["pragma_settings"]
                        pragma_info = []
                        
                        if "foreign_keys" in pragma:
                            fk_status = "ON" if pragma["foreign_keys"] else "OFF"
                            pragma_info.append(f"Foreign Keys: {fk_status}")
                        
                        if "journal_mode" in pragma:
                            journal_mode = pragma["journal_mode"].upper()
                            pragma_info.append(f"Journal: {journal_mode}")
                        
                        if "cache_size" in pragma:
                            # Remove negative sign
                            cache_size = abs(pragma["cache_size"])
                            if cache_size > 1000:
                                cache_display = f"{cache_size // 1000}K pages"
                            else:
                                cache_display = f"{cache_size} pages"
                            pragma_info.append(f"Cache: {cache_display}")
                        
                        if pragma_info:
                            db_content.append(
                                ft.Text(
                                    "Configuration:",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=db_text_color,
                                )
                            )
                            for info in pragma_info:
                                db_content.append(
                                    ft.Text(
                                        f"  • {info}",
                                        size=10,
                                        color=db_text_color,
                                    )
                                )

                    bottom_cards.append(
                        ft.Container(
                            content=ft.Column(db_content, spacing=4),
                            padding=15,
                            bgcolor=db_bg_color,
                            border=ft.border.all(1, ft.Colors.CYAN),
                            border_radius=8,
                            width=300,
                        )
                    )

                details_row.content.controls = bottom_cards

                page.update()

            except Exception as e:
                # Show error in header status
                header.content.controls[1].content = ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("❌", size=18),
                                ft.Text(
                                    "Error",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ERROR,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Text(
                            str(e)[:40] + "..." if len(str(e)) > 40 else str(e),
                            size=10,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=2,
                )
                header.content.controls[1].bgcolor = ft.Colors.SURFACE
                page.update()

        async def auto_refresh() -> None:
            # Wait initial delay before starting auto-refresh cycle
            await asyncio.sleep(30)
            while True:
                await refresh_status()
                await asyncio.sleep(30)

        # Initial load
        await refresh_status()
        # Start auto-refresh task (will wait 30s before first auto-refresh)
        asyncio.create_task(auto_refresh())

    return flet_main
