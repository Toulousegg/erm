import React, { useEffect, useRef, useState } from "react";

import { Login } from "../../dtos/loginDto/loginDto";
import axios from "axios";

export function Login(){
    const URL_BASE = "http://127.0.0.1:8000/home"

    const[usuario, Usuario] = useState<String>();
    const[password, Password] = useState<String>();

    return(
        
    )
}