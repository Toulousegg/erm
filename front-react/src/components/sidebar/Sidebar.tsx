import type { Page } from "../../../dtos/SidebarDto/sidebarDto" //puse ese type porque despues de compilar el codigo esa interfaz no va a existir mas, entonces si intento importarlo no va a existir nada y va a dar error
import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

export function Sidebar() {
    const BASE_URL = "http://127.0.0.1:8000"

    /*este es para decir si el aside esta abierto o no */
    const [collapsed, setCollapsed] = useState(false); /* parece que el useState es para solo darle un valor a una variable y poder cambiarla*/

    /*este para cargar las funciones dependiendo de las que devuelva el backend*/
    const [pages, setPages] = useState<Page[]>([]); //aqui le estoy pasando el tipo que va a ser dentro de los <>, es como en java

    function toggleSidebar() {
        setCollapsed(!collapsed)
    }

    async function request() {
        const response = await axios.get(BASE_URL + "/modules/company", {
            withCredentials: true
        })

        console.log(response)
        console.log(response.data)
        setPages(response.data)
        return response
    }

    useEffect(() => {
        console.log("Hola Mundo!")

        function cargarPages() {
            return request()
        }

        cargarPages()

        if (collapsed) {
            console.log("sidebar desmontado");
            console.log(pages)

        } else {
            console.log("sidebar montado")
            console.log(pages)
        }
    }, []) //lo que esta dentro de estos corchetes en lo que se a verificar para ejecutar lo que este dentro del useEffect, osea, si ese valor cambia se ejecuta el codigo dentro del useEffect

    return (
        <aside className={collapsed ? "sidebar collapsed" : "sidebar"} id="sidebar">
            <div className="sidebar-header">
                <div className="app-icon">
                    <strong>ProntoERP</strong>
                </div>

                <button className="toggle-btn" type="button" onClick={toggleSidebar}>
                    ☰
                </button>
            </div>

            <nav className="sidebar-nav">
                {/* {% for module in modules %} */}
                <a className="nav-item {% if module.route in request.url.path %}active{% endif %}" href="{{ module.route }}">
                    <span className="icon">
                        {/* <img src="{{ module.icon_aside }}" alt="{{ module.name }}"> */}
                    </span>
                    <span className="label">
                        {/* {{ module.name }} */}
                    </span>
                </a>
                {/* {% endfor %} */}


                {pages.map((page) => {
                    return <a className="nav-item" key={page.id} href={page.route}>
                        <span className="icon">
                            <img src={page.icon_aside} alt={page.name} />
                        </span>
                        <span className="label">
                            {page.name}
                        </span>
                    </a>
                })}
            </nav>

            <a className="logout-link" href="/home/login">
                {/* <img src="https://cdn-icons-png.flaticon.com/512/4052/4052024.png" alt="Sair"> */}
                <span>Sair</span>
            </a>
        </aside>
    )
}

export default Sidebar;